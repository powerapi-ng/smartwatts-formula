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

from asyncio.log import logger
import logging
from typing import List, Type, Dict

from prometheus_client import Gauge, Counter

from powerapi.report import Report
from powerapi.database.prometheus_db import BasePrometheusDB

"""
Prometheus Exporter for cloudjoule (powerapi inside k8s)


"""

class CloudJoulePrometheusDB(BasePrometheusDB):

    """
    Database that expose received data as metric in order to be scrapped by a prometheus instance
    Can only be used with a pusher actor.

    The exporter exposes one gauge and one counter metric
    * for rapl energy (total cpu energy usage)
    * for the global energy usage estimated by powerAPI
    * for the estimated energy usage of each pod 
    
    the pod metrics contain:
    * the pod name : `pod_name`
    * the pod namespace : `pod_name_space`
    * the name of the sensor
    * the k8s target (something like `/kubepods/besteffort/pod<uid>/<uid>`)
    * a subset of the k8s labels of the pod 
      * specified using the `tags` argument in the constructor
      * their value is empty for pods that do not have these labels
      * the name id prepended with `label_` . E.g. for a pod holding the k8s label `app=application-2`, the 
        prometheus metric will have a tag `label_app="application-2"`

    Example of the pod energy counter : 
    ```
    cloudjoule_pod_joule_total{label_app="application-2",label_env="",label_k8s_app="",label_service="",pod_name="application-2-5ff95cdbf5-h9xzz",pod_namespace="application-2",sensor="sensor_test",target="/kubepods/besteffort/pod9d7592ea-f1da-4ead-982f-4cd30bb0e1b5/bec1f163e3e1c5ecb019c55034c169df59cd1c489cf276dc4d22e6ab5f1c0bf9"} 0.0
    ```
    """

    def __init__(
        self,
        report_type: Type[Report],
        port: int,
        address: str,
        metric_name: str,
        metric_description: str,
        tags: List[str],
    ):
        """

        Note: here tags will in most cases be the names of k8s labels.

        :param address:             address that expose the metric
        :param port:
        :param metric_name:
        :param metric_description:  short sentence that describe the metric
        :param tags: metadata used to tag metric
        """
        tags += ["pod_name", "pod_namespace", "socket"]
        self.labels_conversion = fix_k8s_labels_names(tags)
        tags = list(self.labels_conversion.values())
        BasePrometheusDB.__init__(
            self, report_type, port, address, metric_name, metric_description, tags
        )

        self.labels_conversion = fix_k8s_labels_names(tags)

        # check for inactive measure every x seconds
        self.CLEANUP_PERIOD = 10
        # if a measure had not update for the last INACTIVE_TIMEOUT seconds, remove it
        self.INACTIVE_TIMEOUT = 60
        # timestamp of the last inactive measures cleanup
        self.cleanup_ts = 0

        self.rapl_counter = None
        self.rapl_gauge = None

        self.global_gauge = None
        self.global_counter = None

        self.pod_counter = None
        self.pod_gauge = None

        # a dict  str -> dict like: { "tag1.tag2....tagn": value}
        # where value is a array of tag, needed to remove the measure from the exporter:
        # [measure["tags"][label] for label in measure["tags"]]
        self.exposed_measure = {}

        # a map measure_key -> ts
        # with for each measure the last ts at which we received an update
        self.measure_last_ts = {}

    def __iter__(self):
        raise NotImplementedError()

    def _init_metrics(self):
        logging.debug(f"init metrics {self.tags}")
        self.rapl_gauge = Gauge(
            f"{self.metric_name}_rapl_power",
            "Gauge for total CPU energy",
            labelnames=["sensor", "socket"],
        )
        self.rapl_counter = Counter(
            f"{self.metric_name}_rapl_joule",
            "Counter for total CPU energy",
            labelnames=["sensor", "socket"],
        )

        self.global_gauge = Gauge(
            f"{self.metric_name}_global_power",
            "Gauge for global estimated energy",
            labelnames=["sensor", "socket"],
        )
        self.global_counter = Counter(
            f"{self.metric_name}_joule",
            "Counter for global estimated energy",
            labelnames=["sensor", "socket"],
        )

        self.pod_gauge = Gauge(
            f"{self.metric_name}_pod_power",
            self.metric_description,
            labelnames=["sensor", "target"] + self.tags,
        )
        self.pod_counter = Counter(
            f"{self.metric_name}_pod_joule",
            self.metric_description,
            labelnames=["sensor", "target"] + self.tags,
        )

    def _expose_data(self, key, measure):

        print(f" _expose_data {measure}")

        logging.debug(f" _expose_data {measure}")

        # select the right gauge, counter and labels depending on the measure
        target = measure["tags"]["target"]
        if target == "rapl":
            gauge = self.rapl_gauge
            counter = self.rapl_counter
            labels = {"sensor": measure["tags"]["sensor"], "socket" : measure["tags"]["socket"]}
        elif target == "global":
            gauge = self.global_gauge
            counter = self.global_counter
            labels = {"sensor": measure["tags"]["sensor"], "socket" : measure["tags"]["socket"]}
        else:
            gauge = self.pod_gauge
            counter = self.pod_counter
            labels = self._fill_tags(measure["tags"])

        # Update gauge and counter
        try: 
            gauge.labels(**labels).set(measure["value"])
            if key in self.measure_last_ts:
                # For counter: take duration since last update into account !
                duration = measure["time"] - self.measure_last_ts[key]
                counter.labels(**labels).inc(measure["value"] * duration)
                self.measure_last_ts[key] = measure["time"]
            else:
                # first report for this measure, we cannot yet compute a consumption
                self.measure_last_ts[key] = measure["time"]
        except ValueError as ve:
            logger.error(f"Cannot publish measure for target {target} : {ve} - {labels} - {measure}")
            print(f"Cannot publish measure for target {target} : {ve} - {labels} - {measure}")

    def save(self, report: Report):
        """
        Override from BaseDB

        :param report: Report to save
        """
        logging.debug(
            f"CLOUDJOULE saving report {report} metadata : -{report.metadata}-"
        )

        self._fix_label_names(report)

        key, measure = self._report_to_measure_and_key(report)
        self._expose_data(key, measure)
        # store exposed measure with associated labels to be able
        # to remove measure that did not receive any update since INACTIVE_TIMEOUT
        self.exposed_measure[key] = list(measure["tags"].values())

        current_ts = measure["time"]
        if current_ts - self.cleanup_ts > self.CLEANUP_PERIOD:
            self._cleanup_measures(current_ts)

    def _cleanup_measures(self, current_ts):
        """
        Remove any measures that had no update during the last
        `INACTIVE_TIMEOUT` seconds
        """
        for key, ts in list(self.measure_last_ts.items()):
            if current_ts - ts > self.INACTIVE_TIMEOUT:
                logging.debug(
                    f"CLOUDJOULE - REMOVE measure inactive for more than {self.INACTIVE_TIMEOUT}s {ts} {current_ts}  {key} "
                )
                args = self.exposed_measure[key]
                try: 
                    self.pod_counter.remove(*args)
                    self.pod_gauge.remove(*args)
                    self.measure_last_ts.pop(key)
                    self.exposed_measure.pop(key)
                except: 
                    pass
            else:
                logging.debug(
                    f"CLOUDJOULE - KEEP measure active < {self.INACTIVE_TIMEOUT}s {ts} {current_ts}  {key} "
                )

        self.cleanup_ts = current_ts

    def save_many(self, reports: List[Report]):
        """
        Save a batch of data

        :param reports: Batch of data.
        """
        for report in reports:
            self.save(report)

    def _fix_label_names(self, report: Report):

        # replace k8s labels names in the report's metadata with their fixed version
        # for prometheus
        for original_name in list(report.metadata):
            if original_name in self.labels_conversion:
                report.metadata[
                    self.labels_conversion[original_name]
                ] = report.metadata.pop(original_name)

    def _fill_tags(self, tags: Dict[str, str]):
        # Prometheus defines tags at the metrics creation time, and they then
        # become mandatory. As we don't want to create a new metrics for each
        # set of tags, we simply add empty value for all missing tags:
        all_tags = tags.copy()
        for k in self.tags:
            if k not in all_tags:
                all_tags[k] = ""
        return all_tags

    def _report_to_measure_and_key(self, report):
        # `report_to_prom` build a dict
        # { 'time': <timestamp_int>,
        #   'value': <power>,
        #   'tags': {
        #     'sensor' : <sensor>, 'target' : <target>, 'label_xx' : 'value' ...
        #   }
        # }
        value = report_to_prom(report, self.tags)

        key = "".join([str(value["tags"][tag]) for tag in value["tags"]])
        return key, value


def report_to_prom(report, tags_keep):
    tags = {"sensor": report.sensor, "target": report.target}
    for metadata_name in tags_keep:
        if metadata_name not in report.metadata:
            # raise BadInputData('no tag ' + metadata_name + ' in power report', self)
            tags[metadata_name] = ""
        else:
            tags[metadata_name] = report.metadata[metadata_name]

    return {
        "tags": tags,
        "time": int(report.timestamp.timestamp()),
        "value": report.power,
    }


def fix_k8s_labels_names(label_names: List[str]) -> Dict[str, str]:
    """
    Fix k8s label names, returns a dict { original_name : fixed_name}.

    When using k8s label names as label names for prometheus, we run into issues
    as they have different rules regarding allowed characters.

    Prometheus:
    * must match regexp `[a-zA-Z_:][a-zA-Z0-9_:]*`
    * https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels

    Kubernetes:
    * "The name segment is required and must be 63 characters or less,
       beginning and ending with an alphanumeric character ([a-z0-9A-Z])
       with dashes (-), underscores (_), dots (.), and alphanumerics between. [...]"
    * https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#syntax-and-character-set

    To avoid this issue we convert characters not allowed in prometheus
    to underscore. We also prepend "label_" in front of the label name.

    With these rules, we can into conflicts when different k8s label names are
    converted to the same prometheus label name. In that case we flag
    these conflicts by adding `_conflict{1}` to the name. This matches
    what is done by kube-state-metrics:

    https://github.com/kubernetes/kube-state-metrics#conflict-resolution-in-label-names

    Note however that we don't add a `"_label"` prefix to the labels
    names here.

    """
    fixed_names = {}
    for label_name in label_names:
        fixed_names[label_name] = fix_k8s_labels_name(label_name)

    # detect and flag conflicts
    names_list = list(fixed_names.values())
    conflicts = [name for name in names_list if names_list.count(name) > 1]
    for conflict in set(conflicts):
        for i, (k, v) in enumerate(list(fixed_names.items())):
            if v == conflict:
                fixed_names[k] = v + f"_conflict{i+1}"

    return fixed_names


def fix_k8s_labels_name(label_name: str) -> str:
    """
    Fix a single k8s label name, see fix_k8s_labels_names for details.
    """
    label_name = label_name.replace("-", "_")
    label_name = label_name.replace(".", "_")
    label_name = label_name.replace("/", "_")
    return label_name
