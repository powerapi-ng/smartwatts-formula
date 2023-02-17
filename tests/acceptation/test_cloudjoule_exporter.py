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

from smartwatts.cloudjoule_exporter import (
    fix_k8s_labels_name,
    fix_k8s_labels_names,
)


def test_supported_labels_are_not_modified():
    assert fix_k8s_labels_name("name_ok_15") == "name_ok_15"


def test_minus_is_replacedin_k8s_labels():
    assert fix_k8s_labels_name("name-ko-15") == "name_ko_15"


def test_dot_is_replacedin_k8s_labels():
    assert fix_k8s_labels_name("name.ko-15") == "name_ko_15"


def test_slash_is_replacedin_k8s_labels():
    assert fix_k8s_labels_name("dd/name.ko-15") == "dd_name_ko_15"


def test_conflicted_names_are_flagged():
    given_names = ["foo-bar", "foo_bar"]

    obtained = fix_k8s_labels_names(given_names)

    assert obtained["foo-bar"] == "foo_bar_conflict1"
    assert obtained["foo_bar"] == "foo_bar_conflict2"


def test_nonconflicted_names_are_not_flagged():
    given_names = ["bar", "foo"]

    obtained = fix_k8s_labels_names(given_names)

    assert obtained["bar"] == "bar"
    assert obtained["foo"] == "foo"


def test_real_names():
    names = ["pod_name", "pod_namespace", "app", "service", "env", "k8s-app"]

    obtained = fix_k8s_labels_names(names)

    assert obtained["pod_name"] == "pod_name"
