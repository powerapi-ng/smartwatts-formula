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

import logging
import re

from powerapi.formula import FormulaActor
from powerapi.handler import PoisonPillMessageHandler
from powerapi.message import PoisonPillMessage
from powerapi.pusher import PusherActor
from powerapi.report import HWPCReport

from smartwatts.handler import ReportHandler, FormulaScope
from smartwatts.topology import CPUTopology


class SmartWattsFormulaActor(FormulaActor):
    """
    This actor handle the reports for the SmartWatts formula.
    """

    def __init__(self, name, power_report_pusher: PusherActor, formula_report_pusher: PusherActor, scope: FormulaScope, rapl_event: str, error_threshold: float, cpu_topology: CPUTopology):
        """
        Initialize the actor.
        :param name: Name of the formula
        :param pusher: Pusher to whom the formula must send its reports
        """
        FormulaActor.__init__(self, name, power_report_pusher, logging.WARNING)
        self.scope = scope
        self.rapl_event = rapl_event
        self.error_threshold = error_threshold
        self.formula_report_pusher = formula_report_pusher
        self.cpu_topology = cpu_topology

        m = re.search(r'^\(\'(.*)\', \'(.*)\', \'(.*)\'\)$', name)  # TODO: Need a better way to get these information
        self.dispatcher = m.group(1)
        self.sensor = m.group(2)
        self.socket = m.group(3)

    def setup(self):
        """
        Setup the actor.
        """
        FormulaActor.setup(self)
        self.add_handler(PoisonPillMessage, PoisonPillMessageHandler())
        self.formula_report_pusher.connect_data()
        handler = ReportHandler(self.sensor, self.actor_pusher, self.formula_report_pusher, self.socket, self.scope, self.rapl_event, self.error_threshold, self.cpu_topology)
        self.add_handler(HWPCReport, handler)
