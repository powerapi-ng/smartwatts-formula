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

import os
import pytest


def test_importing_must_not_fail():
    from smartwatts import configuration


def test_load_config_must_fail_if_missing_mandatory_env():
    from smartwatts import configuration

    # Make sure ate least one required env variable is not defined
    os.environ["MIN_FREQ"] = ""
    with pytest.raises((KeyError, ValueError)):
        configuration.load_config_from_env()


def test_load_must_use_default_value_for_unspecified_nonmandatory_env():
    from smartwatts import configuration

    # Make sure at least one required env variable is not defined
    os.environ["MIN_FREQ"] = "10"
    os.environ["MAX_FREQ"] = "10"
    os.environ["BASE_FREQ"] = "10"
    os.environ["SOCKET_COUNT"] = "1"
    configuration.load_config_from_env()

    assert configuration.REPORT_FREQ == 1000


def test_load_set_conf_from_env():
    from smartwatts import configuration

    os.environ["MIN_FREQ"] = "800"
    os.environ["MAX_FREQ"] = "2000"
    os.environ["BASE_FREQ"] = "1000"
    os.environ["SOCKET_COUNT"] = "1"
    configuration.load_config_from_env()

    assert configuration.MIN_FREQ == 8
    assert configuration.MAX_FREQ == 20
    assert configuration.BASE_FREQ == 10
    assert configuration.SOCKET_COUNT == 1
    assert configuration.REPORT_FREQ == 1000
    assert configuration.ERROR_THRESHOLD == 2
    assert configuration.MIN_SAMPLES_REQUIRED == 10
    assert configuration.HISTORY_WINDOW_SIZE == 60

def test_smartwatt_like_conf():
    from smartwatts import configuration
    os.environ["MIN_FREQ"] = "10"
    os.environ["MAX_FREQ"] = "10"
    os.environ["BASE_FREQ"] = "10"
    os.environ["SOCKET_COUNT"] = "1"
    conf = configuration.get_smartwatt_config_map()

    assert conf is not None

def test_label_conf_from_env():
    from smartwatts import configuration
    os.environ["MIN_FREQ"] = "10"
    os.environ["MAX_FREQ"] = "10"
    os.environ["BASE_FREQ"] = "10"
    os.environ["SOCKET_COUNT"] = "1"    

    # Default value
    configuration.load_config_from_env()
    assert configuration.EXPORTER_LABELS  ==  ["label_app","label_service","label_env"]

    os.environ["EXPORTER_LABELS"] = "label1, label2"    
    configuration.load_config_from_env()
    assert configuration.EXPORTER_LABELS  ==  ["label_label1","label_label2"]
