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

from smartwatts.k8sapi import local_config, k8s_streaming_query, cleanup_container_id

from kubernetes import client


def test_load_local_config():
    # NOTE : this test requires a running k8s cluster !
    local_config()

    # Just check we are able to make a request and get a non-empty response
    v1_api = client.CoreV1Api()
    ret = v1_api.list_pod_for_all_namespaces()
    assert ret.items != []


def test_streaming_query():
    # NOTE : this test requires a running k8s cluster !
    
    def cb(*event):
        print(event)
        assert event is not None

    k8s_streaming_query(cb, 10)

def test_cleanupid_docker():

    r = cleanup_container_id("/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod435532e3_546d_45e2_8862_d3c7b320d2d9.slice/docker-68aa4b590997e0e81257ac4a4543d5b278d70b4c279b4615605bb48812c9944a.scope")

    assert r ==  "68aa4b590997e0e81257ac4a4543d5b278d70b4c279b4615605bb48812c9944a"

def test_cleanupid_othercri():

    r = cleanup_container_id("/kubepods/besteffort/pod42006d2c-cad7-4575-bfa3-91848a558743/ba28184d18d3fc143d5878c7adbefd7d1651db70ca2787f40385907d3304e7f5")

    assert r ==  "ba28184d18d3fc143d5878c7adbefd7d1651db70ca2787f40385907d3304e7f5"    