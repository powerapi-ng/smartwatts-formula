# Copyright (c) 2022, INRIA
# Copyright (c) 2022, University of Lille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# pylint: disable=redefined-outer-name,unused-argument,unused-import,no-self-use

"""
Run smartwatts on a mongodb database that contain 10 hwpc report per target :
- all
- mongodb
- influxdb
- sensor

as the model can't fit with 10 report , it should only return power report for the entire system containing RAPL data

We test if smartwatts return 5 powerReport for rapl target
"""
import time
from datetime import datetime

import pytest

import pymongo

from powerapi.test_utils.unit import shutdown_system
from powerapi.test_utils.db.mongo import mongo_database


from smartwatts.__main__ import run_smartwatts
from smartwatts.test_utils.reports import smartwatts_timeline
from tests.acceptation.acceptation_test_utils import formula_config, formula_config_real_time_enabled, check_db, \
    check_db_real_time, AbstractAcceptationTest


@pytest.fixture
def mongodb_content(smartwatts_timeline):
    """
    Define the content of the input database
    :param smartwatts_timeline: The content of the database
    :return: The content of the database
    """
    return smartwatts_timeline


class TestBasicSmartwattsFormula(AbstractAcceptationTest):
    """
    Execute basic acceptation test for SmartwattsFormula
    """
    def test_normal_behaviour_real_time(self, mongo_database, formula_config_real_time_enabled, shutdown_system):
        """
        Test that the formula generate the expected Power reports when real time is used
        :param mongo_database: The base for executing tests
        :param shutdown_system: Stops the actor system once tests are ended
        """
        supervisor = run_smartwatts(formula_config_real_time_enabled)
        time.sleep(30)

        supervisor.join()
        check_db_real_time()
