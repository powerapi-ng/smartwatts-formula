# Copyright (C) 2021  INRIA
# Copyright (C) 2021  University of Lille
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
#
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from powerapi.report import Report


class FormulaReport(Report):
    """
    FormulaReport stores information about a formula.
    This is useful to gather information about a running formula in order to debug or compute statistics.
    """

    def __init__(self, timestamp: datetime, sensor: str, target: str, metadata: Dict[str, Any]):
        """
        Initialize a Power report using the given parameters.
        :param timestamp: Report timestamp
        :param sensor: Sensor name
        :param target: Target name
        :param metadata: Metadata values, can be anything that add useful information
        """
        Report.__init__(self, timestamp, sensor, target)
        self.metadata = metadata

    def __repr__(self) -> str:
        return 'FormulaReport(%s, %s, %s, %s)' % (self.timestamp, self.sensor, self.target, self.metadata)

    @staticmethod
    def from_json(data: Dict) -> FormulaReport:
        """
        Generate a report using the given data.
        :param data: Dictionary containing the report attributes
        :return: The Formula report initialized with the given data
        """
        return FormulaReport(data['timestamp'], data['sensor'], data['target'], data['metadata'])

    @staticmethod
    def from_mongodb(data: Dict) -> FormulaReport:
        """
        Cast from mongoDB
        """
        return FormulaReport.from_json(data)

    @staticmethod
    def to_mongodb(report: FormulaReport) -> Dict:
        """
        Cast to mongoDB
        """
        return report.__dict__
