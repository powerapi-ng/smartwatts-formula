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

from __future__ import annotations

import logging
import re
from typing import Dict

from powerapi.formula import FormulaActor, FormulaState
from powerapi.handler import PoisonPillMessageHandler
from powerapi.message import PoisonPillMessage
from powerapi.pusher import PusherActor
from powerapi.report import HWPCReport

from smartwatts.handler import ReportHandler, FormulaScope
from smartwatts.topology import CPUTopology


class SmartWattsFormulaConfig:
    """
    Global config of the SmartWatts formula.
    """

    def __init__(self, scope: FormulaScope, rapl_event: str, error_threshold: float, cpu_topology: CPUTopology):
        self.scope = scope
        self.rapl_event = rapl_event
        self.error_threshold = error_threshold
        self.cpu_topology = cpu_topology


class SmartWattsFormulaState(FormulaState):
    """
    State of the SmartWatts formula actor.
    """

    def __init__(self, actor: SmartWattsFormulaActor, pushers: Dict[str, PusherActor], config: SmartWattsFormulaConfig):
        FormulaState.__init__(self, actor, pushers)
        self.config = config

        m = re.search(r'^\(\'(.*)\', \'(.*)\', \'(.*)\'\)$', actor.name)  # TODO: Need a better way to get these information
        self.dispatcher = m.group(1)
        self.sensor = m.group(2)
        self.socket = m.group(3)


class SmartWattsFormulaActor(FormulaActor):
    """
    This actor handle the reports for the SmartWatts formula.
    """

    def __init__(self, name: str, pushers: Dict[str, PusherActor], config: SmartWattsFormulaConfig):
        """
        Initialize a new actor.
        :param name: Name of the actor
        :param power_report_pusher: Pusher for the power reports
        :param formula_report_pusher: Pusher for the formula reports
        :param scope: Scope of the formula
        :param rapl_event: RAPL event to use for reference power consumption
        :param error_threshold: Error threshold triggering the learning
        :param cpu_topology: CPU topology to use
        """
        FormulaActor.__init__(self, name, pushers, logging.WARNING)
        self.state: SmartWattsFormulaState = SmartWattsFormulaState(self, pushers, config)

    def setup(self):
        """
        Setup the messages handlers.
        """
        FormulaActor.setup(self)
        self.add_handler(PoisonPillMessage, PoisonPillMessageHandler(self.state))
        self.add_handler(HWPCReport, ReportHandler(self.state))
