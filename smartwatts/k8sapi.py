# CloudJoule — for powerAPI
#
# Copyright (c) 2022 Orange - All right reserved
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from datetime import timedelta
import logging
from typing import Dict, List, Tuple

from kubernetes import client, config, watch
from kubernetes.client.configuration import Configuration
from kubernetes.client.rest import ApiException

from powerapi.actor import Actor
from powerapi.message import (
    EndMessage,
    Message,
    StartMessage,
)
from powerapi.report import HWPCReport

from thespian.actors import (
    ActorAddress,
    ActorExitRequest,
    ChildActorExited,
    WakeupMessage,
)

"""
This module provides two k8s specific actors
* `K8sMdtModifierActor`, which add k8s metadata to reports 
  and forward them to another actor.
* `K8sMonitorAgent`, which monitors the k8s API and sends 
  messages when pod are created, removed or modified.
  
"""

v1_api = None

LOCAL_CONFIG_MODE = "local"
MANUAL_CONFIG_MODE = "manual"
CLUSTER_CONFIG_MODE = "cluster"

logger = logging.getLogger("node-power-exporter.k8sapi")


def local_config():
    # local kubectl
    config.load_kube_config()


def manual_config():
    # Manual config
    configuration = client.Configuration()
    # Configure API key authorization: BearerToken
    configuration.api_key["authorization"] = "YOUR_API_KEY"
    # Defining host is optional and default to http://localhost
    configuration.host = "http://localhost"
    Configuration.set_default(configuration)


def cluster_config():
    config.load_incluster_config()


def load_k8s_client_config(mode=None):
    """
    Load K8S client configuration according to the `mode`.
    If no mode is given `LOCAL_CONFIG_MODE` is used.

    params:
        mode : one of `LOCAL_CONFIG_MODE`, `MANUAL_CONFIG_MODE`
               or `CLUSTER_CONFIG_MODE`

    """
    logger.debug("Loading k8s api conf mode %s " , mode)
    {
        LOCAL_CONFIG_MODE: local_config,
        MANUAL_CONFIG_MODE: manual_config,
        CLUSTER_CONFIG_MODE: cluster_config,
    }.get(mode, local_config)()


def get_core_v1_api(mode=None):
    """
    Returns an handle to the k8s API.
    """
    global v1_api
    if v1_api is None:
        load_k8s_client_config(mode)
        v1_api = client.CoreV1Api()
        print(f"Core v1 api access : {v1_api}")
    return v1_api


class K8sMdtModifierStartMessage(StartMessage):
    """Start Message for K8sMdtModifierActor"""
    def __init__(self, sender_name: str, name: str, forward_actor: str, k8sapi_mode: str):
        """
        :param forward_actor address of the agent the K8sMdtModifierActor will
               forward modified messages to.
        """
        StartMessage.__init__(self, sender_name, name)
        self.forward_actor = forward_actor
        self.k8sapi_mode = k8sapi_mode

    def __str__(self):
        return "K8sMdtModifierStartMessage"


class K8sPodUpdateMessage(Message):
    """Message sent by the K8sMonitorAgent everytime it detects a change
       on pod in K8S.
    """
    def __init__(
        self,
        sender_name: str,
        event: str,
        namespace: str,
        pod: str,
        containers_id: List[str] = None,
        labels: Dict[str, str] = None,
    ):
        """

        :param datetime timestamp: Timestamp
        :param str sensor: Sensor name.
        :param str target: Target name.
        """
        Message.__init__(self, sender_name)
        self.event = event
        self.namespace = namespace
        self.pod = pod
        self.containers_id = containers_id if containers_id is not None else []
        self.labels = labels if labels is not None else dict()

    def __str__(self):
        return f"K8sPodUpdateMessage {self.event} {self.namespace} {self.pod}"


class K8sMdtModifierActor(Actor):
    """
    Add k8s metadata to reports and forward them to another actor.

    Metadata is a dict on the report, if the target of the report
    is a container that we can associate to a pod, we add:
    * '"pod_name" : <name_of_the_pod>`
    * '"pod_namespace" : <namespane_of_the_pod>`
    * '"label_"<label_name> : <label_value>` for each label on the pod

    If the target of the report cannot be associated to a pod
    (e.g. `rapl` or `all` targets) no metadata is added.

    To avoid querying k8s API for each report, this actor maintains a cache
    of k8s  pod meta-data information. The cache is kept up-to-date thanks
    to messages from the `K8sMonitorAgent`.
    """

    def __init__(self):
        Actor.__init__(self, K8sMdtModifierStartMessage)
        self.log_debug("Init K8sMdtModifierActor")
        self.forward_actor = None
        self.mdt_cache = None
        self.monitor_agent = None

    def _initialization(self, start_message: StartMessage):
        self.log_debug("Initializing K8s Modifier actor")
        Actor._initialization(self, start_message)
        self.log_debug("Initializing K8s Modifier actor")
        self.mdt_cache = K8sMdtCache()

        self.forward_actor = start_message.forward_actor
        # Create monitor agent:
        self.log_debug("Creating monitor agent")
        self.monitor_agent = self.createActor(K8sMonitorAgent)
        self.log_debug("Sending start to monitor agent")
        self.send(
            self.monitor_agent,
            K8sMonitorStartMessage(
                self.name,
                "k8s_monitor_agent",
                self.myAddress,
                start_message.k8sapi_mode),
        )

    def receiveMsg_EndMessage(self, message: EndMessage, _: ActorAddress):
        """
        when receiving a EndMessage kill itself
        """
        self.log_debug("K8sMdtModifierActor received message " + str(message))

        self.send(self.forward_actor, EndMessage(self.name))
        self.send(self.myAddress, ActorExitRequest())

    def receiveMsg_K8sPodUpdateMessage(self, message, _: ActorAddress):

        self.log_debug(f"received K8sPodUpdateMessage message {message}")
        self.mdt_cache.update_cache(message)

    def receiveMsg_ChildActorExited(
            self,
            _msg: ChildActorExited,
            _: ActorAddress):
        self.log_error("Error Child agent K8S monitor failed")

    def receiveMsg_OKMessage(self, message, _: ActorAddress):
        # received when the Monitor agent has been started successfully
        pass

    def receiveMsg_HWPCReport(self, message: HWPCReport, _):

        # Add pod name, namespace and labels to the report
        c_id = cleanup_container_id(message.target)
        ns, pod = self.mdt_cache.get_container_pod(c_id)
        if ns is None or pod is None:
            self.log_warning(
                f"Container with no associated pod : {message.target}, {c_id}, {ns}, {pod}" 
            )
            # self.log_debug(f"MDT_CACHE DUMP : {self.mdt_cache.pod_containers} \n "
            #                f" {self.mdt_cache.containers_pod} \n" 
            #                f" {self.mdt_cache.pod_labels} ")
        else:
            message.metadata["pod_namespace"] = ns
            message.metadata["pod_name"] = pod
            self.log_debug(
                f"K8sMdtModifierActor add mdt to report {c_id}, {ns}, {pod}"
            )

            labels = self.mdt_cache.get_pod_labels(ns, pod)
            for label_key, label_value in labels.items():
                message.metadata[f"label_{label_key}"] = label_value

        self.send(self.forward_actor, message)


class K8sMdtCache:
    """
    K8sMdtCache maintains a cache of pods' metadata
    (namespace, labels and id of associated containers)
    """
    def __init__(self):
        self.pod_labels = dict() # (ns, pod) => [labels]
        self.containers_pod = dict() # container_id => (ns, pod)
        self.pod_containers = dict() # (ns, pod) => [container_ids]

    def update_cache(self, message: K8sPodUpdateMessage):
        """
        Update the local cache for pods.

        Register this function as a callback for K8sMonitorAgent messages.
        """
        if message.event == "ADDED":
            self.pod_labels[(message.namespace, message.pod)] = message.labels
            self.pod_containers[
                (message.namespace, message.pod)
            ] = message.containers_id
            for container_id in message.containers_id:
                self.containers_pod[container_id] = \
                    (message.namespace, message.pod)
            # logger.debug(
            #     "Pod added  %s %s - mdt: %s",
            #     message.namespace, message.pod, message.containers_id
            # )

        elif message.event == "DELETED":
            self.pod_labels.pop((message.namespace, message.pod), None)
            for container_id in self.pod_containers.pop(
                (message.namespace, message.pod), []
            ):
                self.containers_pod.pop(container_id, None)
            # logger.debug("Pod removed %s %s", message.namespace, message.pod)

        elif message.event == "MODIFIED":
            self.pod_labels[(message.namespace, message.pod)] = message.labels
            for prev_container_id in self.pod_containers.pop(
                (message.namespace, message.pod), []
            ):
                self.containers_pod.pop(prev_container_id, None)
            self.pod_containers[
                (message.namespace, message.pod)
            ] = message.containers_id
            for container_id in message.containers_id:
                self.containers_pod[container_id] = \
                    (message.namespace, message.pod)

            # logger.debug(
            #     "Pod modified %s %s , mdt: %s",
            #     message.namespace, message.pod, message.containers_id
            # )
        else:
            logger.error("Error : unknown event type %s ", message.event)

    def get_container_pod(self, container_id) -> Tuple[str, str]:
        """
        Get the pod for a container_id.

        :param container_id
        :return a tuple (namespace, pod_name) of (None, None) if no pod
                could be found for this container
        """
        ns_pod = self.containers_pod.get(container_id, None)
        if ns_pod is None:
            return None, None
        return ns_pod

    def get_pod_labels(self, namespace: str, pod_name: str) -> Dict[str, str]:
        """
        Get labels for a pod.

        :param namespace
        :param
        :return a dict {label_name, label_value}
        """
        return self.pod_labels.get((namespace, pod_name), dict)


class K8sMonitorStartMessage(StartMessage):
    def __init__(self, sender_name, name, listener_agent, k8sapi_mode):
        """
        :param listener_agent the agent `K8sMonitorAgent` must
                              send it's event to.
        """
        StartMessage.__init__(self, sender_name, name)
        self.listener_agent = listener_agent
        self.k8sapi_mode = k8sapi_mode

    def __str__(self):
        return "K8sMonitorStartMessage"


class K8sMonitorAgent(Actor):
    """
    An actor that monitors the k8s API and sends messages
    when pod are created, removed or modified.
    """

    def __init__(self):
        """
        :param period: time in second, between to k8s pooling
        """
        Actor.__init__(self, K8sMonitorStartMessage)
        self._time_interval = timedelta(seconds=10)
        self.timeout_query = 5
        self.listener_agent = None
        self.k8sapi_mode = None

    def _initialization(self, start_message: K8sMonitorStartMessage):
        Actor._initialization(self, start_message)
        self.listener_agent = start_message.listener_agent
        self.k8sapi_mode = start_message.k8sapi_mode
        self.log_warning("setup initial wakeup timer ")
        self.wakeupAfter(self._time_interval)

    def _query_k8s(self):
        try:
            events = k8s_streaming_query(self.timeout_query, self.k8sapi_mode)
            for event in events:
                event_type, namespace, pod_name, container_ids, labels = event
                self.send(
                    self.listener_agent,
                    K8sPodUpdateMessage(
                        self.name,
                        event_type,
                        namespace,
                        pod_name,
                        container_ids,
                        labels
                    )
                )
        except Exception as ex:
            self.log_warning(ex)
            self.log_warning(f"Failed streaming query {ex}")

    def receiveMsg_WakeupMessage(self, _: WakeupMessage, __: ActorAddress):
        """
        When receiving a WakeupMessage, launch the actor task
        """
        self.log_debug("Wakeup - K8sMonitorAgent Querying k8s")
        self._query_k8s()
        self.log_debug("K8sMonitorAgent Streaming finished, wait until next timer")
        self.wakeupAfter(self._time_interval)

    def receiveMsg_EndMessage(self, message: EndMessage, _: ActorAddress):
        """
        when receiving a EndMessage kill itself
        """
        self.log_debug("received message " + str(message))
        self.send(self.myAddress, ActorExitRequest())


def k8s_streaming_query(timeout_seconds, k8sapi_mode):
    v1_api = get_core_v1_api(k8sapi_mode)
    events = []
    w = watch.Watch()
    # FIXME : handle node name
    logger.debug(f"Waiting for events on pods with timeout {timeout_seconds}")
    try:
        for event in w.stream(
            v1_api.list_pod_for_all_namespaces, timeout_seconds=timeout_seconds
        ):
            if not event["type"] in {"DELETED", "ADDED", "MODIFIED"}:
                logger.warning(
                    "UNKNOWN EVENT TYPE : %s :  %s  %s",
                    event['type'], event['object'].metadata.name, event
                )
                continue
            pod_obj = event["object"]
            namespace, pod_name = \
                pod_obj.metadata.namespace, pod_obj.metadata.name
            container_ids = (
                [] if event["type"] == "DELETED"
                else extract_containers(pod_obj)
            )
            labels = pod_obj.metadata.labels
            events.append(
                (event["type"], namespace, pod_name, container_ids, labels)
            )

    except ApiException as ae:
        logger.error(f"APIException {ae.status} {ae}", ae)
    except Exception as undef_e:
        logger.error(f"Error when watching Exception '{undef_e}' {event}")
    return events


def extract_containers(pod_obj):
    # print(pod_obj)
    if not pod_obj.status.container_statuses:
        return []

    container_ids = []
    for container_status in pod_obj.status.container_statuses:
        container_id = container_status.container_id
        if not container_id:
            continue
        # container_id actually depends on the container engine used by k8s.
        # It seems that is always start with <something>://<actual_id>
        # e.g.
        # 'containerd://2289b494f36b93647cfefc6f6ed4d7f36161d5c2f92d1f23571878a4e85282ed'
        container_id = container_id[container_id.index("//") + 2:]
        container_ids.append(container_id)

    return sorted(container_ids)


def cleanup_container_id(c_id):
    # On some system, we receive a container id that requires some cleanup to match
    # the id returned by the k8s api
    # k8s creates cgroup directories, which is what we get as id from the sensor,
    # according to this pattern :
    #     /kubepods/<qos>/pod<pod-id>/<containerId>
    # depending on the container engine, we need to cleanup the <containerId> part

    if "/docker-" in c_id:
        # for path like :
        # /kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod435532e3_546d_45e2_8862_d3c7b320d2d9.slice/docker-68aa4b590997e0e81257ac4a4543d5b278d70b4c279b4615605bb48812c9944a.scope
        # where we actually only want the end of that path :
        # 68aa4b590997e0e81257ac4a4543d5b278d70b4c279b4615605bb48812c9944a
        try:
            return c_id[c_id.rindex("/docker-") + 8: -6]
        except ValueError:
            return c_id
    else:
        # /kubepods/besteffort/pod42006d2c-cad7-4575-bfa3-91848a558743/ba28184d18d3fc143d5878c7adbefd7d1651db70ca2787f40385907d3304e7f5
        try:
            return c_id[c_id.rindex("/") + 1:]
        except ValueError:
            return c_id
