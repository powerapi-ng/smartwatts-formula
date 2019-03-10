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
from powerapi.report import HWPCReport

from smartwatts.handler import ReportHandler, FormulaScope


class SmartWattsFormulaActor(FormulaActor):
    """
    This actor handle the reports for the SmartWatts formula.
    """

    def __init__(self, name, pusher, scope: FormulaScope, rapl_event: str, error_threshold: float):
        """
        Initialize the actor.
        :param name: Name of the formula
        :param pusher: Pusher to whom the formula must send its reports
        """
        FormulaActor.__init__(self, name, pusher, logging.WARNING)
        self.scope = scope
        self.rapl_event = rapl_event
        self.error_threshold = error_threshold

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
        handler = ReportHandler(self.sensor, self.actor_pusher, self.socket, self.scope, self.rapl_event, self.error_threshold)
        self.add_handler(HWPCReport, handler)
