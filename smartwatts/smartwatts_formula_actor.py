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
import logging
from enum import Enum
from typing import Dict
from collections import OrderedDict

from powerapi.handler import StartHandler
from powerapi.pusher import PusherActor

from powerapi.formula import AbstractCpuDramFormula
from powerapi.message import PoisonPillMessage, StartMessage
from powerapi.report import HWPCReport

from .smartwatts_handlers import ReportHandler, SmartWattsFormulaPoisonPillMessageHandler


class SmartWattsFormulaScope(Enum):
    """
    Enum used to set the scope of the SmartWatts formula.
    """
    CPU = "cpu"
    DRAM = "dram"


class SmartWattsFormulaConfig:
    """
    Global config of the SmartWatts formula.
    """

    def __init__(self, scope, reports_frequency, rapl_event, error_threshold, cpu_topology, min_samples_required,
                 history_window_size, real_time_mode):
        """
        Initialize a new formula config object.
        :param scope: Scope of the formula
        :param reports_frequency: Frequency at which the reports (in milliseconds)
        :param rapl_event: RAPL event to use as reference
        :param error_threshold: Error threshold (in Watt)
        :param cpu_topology: Topology of the CPU
        :param min_samples_required: Minimum amount of samples required before trying to learn a power model
        :param history_window_size: Size of the history window used to keep samples to learn from
        """
        self.scope = scope
        self.reports_frequency = reports_frequency
        self.rapl_event = rapl_event
        self.error_threshold = error_threshold
        self.cpu_topology = cpu_topology
        self.min_samples_required = min_samples_required
        self.history_window_size = history_window_size
        self.real_time_mode = real_time_mode


class SmartWattsFormulaActor(AbstractCpuDramFormula):
    """
    This actor handle the reports for the SmartWatts formula.
    """

    def __init__(self, name: str, power_pushers: Dict[str, PusherActor], formula_pushers: Dict[str, PusherActor],
                 socket: str, core: str, config: SmartWattsFormulaConfig, sensor: str, level_logger=logging.WARNING,
                 timeout=None):
        AbstractCpuDramFormula.__init__(self, name, power_pushers, socket, core, level_logger, timeout)

        self.state.config = config
        self.state.sensor = sensor
        self.state.ticks = OrderedDict()
        # self.formula = None
        self.state.formula_pushers = formula_pushers
        # self.real_time_mode = None

    def setup(self):
        """
        Initialize Handler
        """
        AbstractCpuDramFormula.setup(self)
        self.add_handler(PoisonPillMessage, SmartWattsFormulaPoisonPillMessageHandler(self.state))
        self.add_handler(HWPCReport, ReportHandler(self.state))
        self.add_handler(StartMessage, StartHandler(self.state))
