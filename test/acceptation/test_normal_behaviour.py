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

as the model can't fit with 10 report , it should only return power report for the entire system containing RAPL data
"""
import pytest

import pymongo

from smartwatts.__main__ import run_smartwatts

from test.mongo_utils import gen_base_db_test
from test.mongo_utils import clean_base_db_test


DB_URI = "mongodb://localhost:27017/"

@pytest.fixture
def database():
    db = gen_base_db_test(DB_URI, 10)
    yield db
    clean_base_db_test(DB_URI)


def check_db():
    mongo = pymongo.MongoClient(DB_URI)
    c_input = mongo['MongoDB1']['test_hwrep']
    c_output = mongo['MongoDB1']['test_result']

    assert c_output.count_documents({}) == (c_input.count_documents({}) / 4) - 5

    for report in c_input.find()[:20]:
        if report['target'] == 'all':
            query = {'timestamp': report['timestamp'], 'sensor': report['sensor'],
                 'target': 'rapl'}
            assert c_output.count_documents(query) == 1


def test_normal_behaviour(database):
    config = {'verbose': 0,
              'stream': False,
              'input': {'mongodb': {'puller_mongodb': {'name': 'puller_mongodb', 'model': 'HWPCReport', 'uri': DB_URI,
                                                       'db': 'MongoDB1', 'collection': 'test_hwrep'}}},
              'output': {'mongodb': {'power': {'model': 'PowerReport', 'name': 'power', 'uri': DB_URI, 'db': 'MongoDB1',
                                               'collection': 'test_result'},
                                     'formula': {'model': 'FormulaReport', 'name': 'formula', 'uri': DB_URI,
                                                 'db': 'MongoDB1', 'collection': 'test_result_formula'}}},
              'formula': {'smartwatts': {'disable-cpu-formula': False, 'disable-dram-formula': True, 'cpu-rapl-ref-event': 'RAPL_ENERGY_PKG',
                                          'cpu-tdp': 125, 'cpu-base-clock': 100, 'cpu-ratio-min': 4, 'cpu-ratio-base': 19, 'cpu-ratio-max': 42,
                                          'cpu-error-threshold': 2.0, 'sensor-reports-frequency': 1000, 'learn-min-samples-required': 10,
                                          'learn-history-window-size': 60}}}

    run_smartwatts(config)
    check_db()
