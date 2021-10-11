# Copyright (C) 2018  INRIA
# Copyright (C) 2018  University of Lille
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Run smartwatts on a mongodb database that contain 10 hwpc report per target

- all
- mongodb
- influxdb
- sensor
The first hwpc report contains mperf value equals to 0
Test if the system don't crash after receiving the first report and deal with the other report
"""
from datetime import datetime
import pytest

import pymongo

from smartwatts.__main__ import run_smartwatts
from smartwatts.test_utils.reports import smartwatts_timeline_with_mperf_0, smartwatts_timeline
from powerapi.test_utils.actor import shutdown_system
from powerapi.test_utils.db.mongo import mongo_database
from powerapi.test_utils.db.mongo import MONGO_URI, MONGO_INPUT_COLLECTION_NAME, MONGO_OUTPUT_COLLECTION_NAME, MONGO_DATABASE_NAME

@pytest.fixture
def mongodb_content(smartwatts_timeline_with_mperf_0):
    return smartwatts_timeline_with_mperf_0


def check_db():
    mongo = pymongo.MongoClient(MONGO_URI)
    c_input = mongo[MONGO_DATABASE_NAME][MONGO_INPUT_COLLECTION_NAME]
    c_output = mongo[MONGO_DATABASE_NAME][MONGO_OUTPUT_COLLECTION_NAME]

    assert c_output.count_documents({}) == (c_input.count_documents({}) / 4) - 6

    for report in c_input.find({'target':'all'})[1:5]:
        ts = datetime.strptime(report['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
        query = {'timestamp': ts, 'sensor': report['sensor'],
                 'target': 'rapl'}
        assert c_output.count_documents(query) == 1


def test_normal_behaviour(mongo_database, shutdown_system):
    config = {'verbose': 0,
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
              'cpu-ratio-min': 4,
              'cpu-ratio-base': 19,
              'cpu-ratio-max': 42,
              'cpu-error-threshold': 2.0,
              'sensor-report-sampling-interval': 1000,
              'learn-min-samples-required': 10,
              'learn-history-window-size': 60,
              'real-time-mode': False}

    run_smartwatts(config)
    check_db()
