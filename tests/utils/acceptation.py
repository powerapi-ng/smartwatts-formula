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

# pylint: disable=redefined-outer-name,unused-argument,unused-import
import time
from datetime import datetime
from multiprocessing import active_children

import pymongo
import pytest

from tests.utils.db.mongo import MONGO_URI, MONGO_DATABASE_NAME, MONGO_INPUT_COLLECTION_NAME, \
    MONGO_OUTPUT_COLLECTION_NAME, gen_base_db_test, clean_base_db_test

from smartwatts.__main__ import run_smartwatts

TICKS_NUMBER = 5
REALTIME_TICKS_NUMBER = 2
SENSOR_NAME = 'cpu'


def check_db():
    """
    Check that the output database has the generated reports
    """
    mongo = pymongo.MongoClient(MONGO_URI)
    c_input = mongo[MONGO_DATABASE_NAME][MONGO_INPUT_COLLECTION_NAME]
    c_output = mongo[MONGO_DATABASE_NAME][MONGO_OUTPUT_COLLECTION_NAME]

    assert c_output.count_documents({}) == (c_input.count_documents({}) / 4) - TICKS_NUMBER

    for report in c_input.find({'target': 'all'})[1:5]:
        ts = datetime.strptime(report['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
        query = {'timestamp': ts, 'sensor': SENSOR_NAME,
                 'target': 'rapl'}
        assert c_output.count_documents(query) == 1


def check_db_real_time():
    """
    Check that the output database has the generated reports
    """
    mongo = pymongo.MongoClient(MONGO_URI)
    c_input = mongo[MONGO_DATABASE_NAME][MONGO_INPUT_COLLECTION_NAME]
    c_output = mongo[MONGO_DATABASE_NAME][MONGO_OUTPUT_COLLECTION_NAME]

    assert c_output.count_documents({}) == (c_input.count_documents({}) / 4) - REALTIME_TICKS_NUMBER

    for report in c_input.find({'target': 'all'})[:5]:
        ts = datetime.strptime(report['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
        query = {'timestamp': ts, 'sensor': SENSOR_NAME,
                 'target': 'rapl'}
        assert c_output.count_documents(query) == 1


class AbstractAcceptationTest:
    """
    Basic acceptation tests for SmartWatts Formula
    """

    @pytest.fixture
    def shutdown_system(self):
        """
        Shutdown the actor system, i.e., all actors are killed
        """
        yield None
        active = active_children()
        for child in active:
            child.kill()

    @pytest.fixture
    def mongo_database(self, mongodb_content):
        """
        connect to a local mongo database (localhost:27017) and store data contained in the list influxdb_content
        after test end, delete the data
        """
        gen_base_db_test(MONGO_URI, mongodb_content)
        yield None
        clean_base_db_test(MONGO_URI)

    @pytest.fixture
    def formula_config(self):
        """
        Return a formula config
        :return: The formula config
        """
        return {'verbose': 0,
                'stream': False,
                'input': {'puller_mongodb': {'type': 'mongodb',
                                             'model': 'HWPCReport',
                                             'uri': MONGO_URI,
                                             'db': MONGO_DATABASE_NAME,
                                             'collection': MONGO_INPUT_COLLECTION_NAME}},
                'output': {'power_pusher': {'type': 'mongodb',
                                            'model': 'PowerReport',
                                            'uri': MONGO_URI,
                                            'db': MONGO_DATABASE_NAME,
                                            'collection': MONGO_OUTPUT_COLLECTION_NAME},
                           'formula_pusher': {'type': 'mongodb',
                                              'model': 'FormulaReport',
                                              'uri': MONGO_URI,
                                              'db': MONGO_DATABASE_NAME,
                                              'collection': 'test_result_formula'}},
                'disable-cpu-formula': False,
                'disable-dram-formula': True,
                'cpu-rapl-ref-event': 'RAPL_ENERGY_PKG',
                'cpu-tdp': 125,
                'cpu-base-clock': 100,
                'cpu-frequency-min': 4,
                'cpu-frequency-base': 19,
                'cpu-frequency-max': 42,
                'cpu-error-threshold': 2.0,
                'sensor-report-sampling-interval': 1000,
                'learn-min-samples-required': 10,
                'learn-history-window-size': 60,
                'real-time-mode': False}

    @pytest.fixture
    def formula_config_real_time_enabled(self, formula_config):
        """
        Return a formula config with real time mode = True
        :return: The formula config
        """
        formula_config['real-time-mode'] = True
        return formula_config

    def test_normal_behaviour(self, mongo_database, formula_config, shutdown_system):
        """
        Test that the formula generate the expected Power reports
        :param mongo_database: The base for executing tests
        :param shutdown_system: Stops the actor system once tests are ended
        """
        supervisor = run_smartwatts(formula_config)
        time.sleep(30)
        supervisor.join()
        check_db()
