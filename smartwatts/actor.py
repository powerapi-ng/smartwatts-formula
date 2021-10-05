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
from typing import Dict
from collections import OrderedDict, defaultdict
from math import ldexp, fabs

from thespian.actors import ActorAddress
from sklearn.exceptions import NotFittedError

from powerapi.formula import AbstractCpuDramFormula, FormulaValues
from powerapi.message import FormulaStartMessage, EndMessage
from powerapi.report import HWPCReport, PowerReport

from .report import FormulaReport
from .context import SmartWattsFormulaConfig
from .formula import SmartWattsFormula


class SmartwattsValues(FormulaValues):
    """
    Initialize smartwatts values
    """
    def __init__(self, formula_pushers: Dict[str, ActorAddress], power_pushers: Dict[str, ActorAddress], config: SmartWattsFormulaConfig):
        """
        :param pushers: Pusher actors
        :param config: Configuration of the formula
        """
        FormulaValues.__init__(self, power_pushers)
        self.config = config
        self.formula_pushers = formula_pushers


class SmartWattsFormulaActor(AbstractCpuDramFormula):
    """
    This actor handle the reports for the SmartWatts formula.
    """

    def __init__(self):
        AbstractCpuDramFormula.__init__(self, FormulaStartMessage)

        self.config = None
        self.ticks = None
        self.formula = None
        self.formula_pushers = None
        self.real_time_mode = None

    def _initialization(self, message: FormulaStartMessage):
        AbstractCpuDramFormula._initialization(self, message)
        self.config = message.values.config
        self.formula_pushers = message.values.formula_pushers
        self.ticks = OrderedDict()
        self.formula = SmartWattsFormula(self.config.cpu_topology, self.config.history_window_size)
        self.real_time_mode = self.config.real_time_mode

    def receiveMsg_HWPCReport(self, message: HWPCReport, _):
        """
        Process a HWPC report and send the result(s) to a pusher actor.
        :param msg: Received message
        :param state: Current actor state
        :return: New actor state
        :raise: UnknowMessageTypeException when the given message is not an HWPCReport
        """
        self.log_debug('received message ' + str(message))
        self.ticks.setdefault(message.timestamp, {}).update({message.target: message})

        # start to process the oldest tick only after receiving at least 5 ticks.
        # we wait before processing the ticks in order to mitigate the possible delay of the sensor/database.
        if self.real_time_mode:
            if len(self.ticks) > 2:
                power_reports, formula_reports = self._process_oldest_tick()
                for report in power_reports:
                    for name, pusher in self.pushers.items():
                        self.send(pusher, report)
                        self.log_debug('send ' + str(report) + ' to ' + name)
                for report in formula_reports:
                    for name, pusher in self.formula_pushers.items():
                        self.send(pusher, report)
                        self.log_debug('send ' + str(report) + ' to ' + name)

        else:
            if len(self.ticks) > 5:
                power_reports, formula_reports = self._process_oldest_tick()
                for report in power_reports:
                    for name, pusher in self.pushers.items():
                        self.send(pusher, report)
                        self.log_debug('send ' + str(report) + ' to ' + name)
                for report in formula_reports:
                    for name, pusher in self.formula_pushers.items():
                        self.send(pusher, report)
                        self.log_debug('send ' + str(report) + ' to ' + name)

    def receiveMsg_EndMessage(self, message: EndMessage, sender: ActorAddress):
        """
        when receiving a EndMessage kill itself and send an EndMessage to all formula pushers
        """
        AbstractCpuDramFormula.receiveMsg_EndMessage(self, message, sender)
        for _, pusher in self.formula_pushers.items():
            self.send(pusher, EndMessage(self.name))

    def _process_oldest_tick(self):
        """
        Process the oldest tick stored in the stack and generate power reports for the running target(s).
        :return: Power reports of the running target(s)
        """
        timestamp, hwpc_reports = self.ticks.popitem(last=False)

        # reports of the current tick
        power_reports = []
        formula_reports = []

        # prepare required events group of Global target
        try:
            global_report = hwpc_reports.pop('all')
        except KeyError:
            # cannot process this tick without the reference measurements
            return power_reports, formula_reports

        rapl = self._gen_rapl_events_group(global_report)
        avg_msr = self._gen_msr_events_group(global_report)
        global_core = self._gen_agg_core_report_from_running_targets(hwpc_reports)

        # compute RAPL power report
        rapl_power = rapl[self.config.rapl_event]
        power_reports.append(self._gen_power_report(timestamp, 'rapl', self.config.rapl_event, 0.0, rapl_power, 1.0))

        if global_core == {}:
            return power_reports, formula_reports

        # fetch power model to use
        pkg_frequency = self.formula.compute_pkg_frequency(avg_msr)
        model = self.formula.get_power_model(avg_msr)

        # compute Global target power report
        try:
            raw_global_power = model.compute_power_estimation(global_core)
            power_reports.append(self._gen_power_report(timestamp, 'global', model.hash, raw_global_power, raw_global_power, 1.0))
        except NotFittedError:
            model.store_report_in_history(rapl_power, global_core)
            model.learn_power_model(self.config.min_samples_required, 0.0, self.config.cpu_topology.tdp)
            return power_reports, formula_reports

        # compute per-target power report
        for target_name, target_report in hwpc_reports.items():
            target_core = self._gen_core_events_group(target_report)
            raw_target_power = model.compute_power_estimation(target_core)
            target_power, target_ratio = model.cap_power_estimation(raw_target_power, raw_global_power)
            target_power = model.apply_intercept_share(target_power, target_ratio)
            power_reports.append(self._gen_power_report(timestamp, target_name, model.hash, raw_target_power, target_power, target_ratio))

        # compute power model error from reference
        model_error = fabs(rapl_power - raw_global_power)

        # store global report
        model.store_report_in_history(rapl_power, global_core)

        # learn new power model if error exceeds the error threshold
        if model_error > self.config.error_threshold:
            model.learn_power_model(self.config.min_samples_required, 0.0, self.config.cpu_topology.tdp)

        # store information about the power model used for this tick
        formula_reports.append(self._gen_formula_report(timestamp, pkg_frequency, model, model_error))
        return power_reports, formula_reports

    def _gen_formula_report(self, timestamp, pkg_frequency, model, error):
        """
        Generate a formula report using the given parameters.
        :param timestamp: Timestamp of the measurements
        :param pkg_frequency: Package average frequency
        :param model: Power model used for the estimation
        :param error: Error rate of the model
        :return: Formula report filled with the given parameters
        """
        metadata = {
            'scope': self.config.scope.value,
            'socket': self.socket,
            'layer_frequency': model.frequency,
            'pkg_frequency': pkg_frequency,
            'samples': len(model.history),
            'id': model.id,
            'error': error,
            'intercept': model.model.intercept_,
            'coef': str(model.model.coef_)
        }
        return FormulaReport(timestamp, self.sensor, model.hash, metadata)

    def _gen_power_report(self, timestamp, target, formula, raw_power, power, ratio):
        """
        Generate a power report using the given parameters.
        :param timestamp: Timestamp of the measurements
        :param target: Target name
        :param formula: Formula identifier
        :param power: Power estimation
        :return: Power report filled with the given parameters
        """
        metadata = {
            'scope': self.config.scope.value,
            'socket': self.socket,
            'formula': formula,
            'ratio': ratio,
            'predict': raw_power,
        }
        return PowerReport(timestamp, self.sensor, target, power, metadata)

    def _gen_rapl_events_group(self, system_report):
        """
        Generate an events group with the RAPL reference event converted in Watts for the current socket.
        :param system_report: The HWPC report of the System target
        :return: A dictionary containing the RAPL reference event with its value converted in Watts
        """
        cpu_events = next(iter(system_report.groups['rapl'][str(self.socket)].values()))
        energy = ldexp(cpu_events[self.config.rapl_event], -32) / (self.config.reports_frequency / 1000)
        return {self.config.rapl_event: energy}

    def _gen_msr_events_group(self, system_report):
        """
        Generate an events group with the average of the MSR counters for the current socket.
        :param system_report: The HWPC report of the System target
        :return: A dictionary containing the average of the MSR counters
        """
        msr_events_group = defaultdict(int)
        msr_events_count = defaultdict(int)
        for _, cpu_events in system_report.groups['msr'][str(self.socket)].items():
            for event_name, event_value in {k: v for k, v in cpu_events.items() if not k.startswith('time_')}.items():
                msr_events_group[event_name] += event_value
                msr_events_count[event_name] += 1
        return {k: (v / msr_events_count[k]) for k, v in msr_events_group.items()}

    def _gen_core_events_group(self, report):
        """
        Generate an events group with Core events for the current socket.
        The events value are the sum of the value for each CPU.
        :param report: The HWPC report of any target
        :return: A dictionary containing the Core events of the current socket
        """
        core_events_group = defaultdict(int)
        for _, cpu_events in report.groups['core'][str(self.socket)].items():
            for event_name, event_value in {k: v for k, v in cpu_events.items() if not k.startswith('time_')}.items():
                core_events_group[event_name] += event_value

        return core_events_group

    def _gen_agg_core_report_from_running_targets(self, targets_report):
        """
        Generate an aggregate Core events group of the running targets for the current socket.
        :param targets_report: List of Core events group of the running targets
        :return: A dictionary containing an aggregate of the Core events for the running targets of the current socket
        """
        agg_core_events_group = defaultdict(int)
        for _, target_report in targets_report.items():
            for event_name, event_value in self._gen_core_events_group(target_report).items():
                agg_core_events_group[event_name] += event_value

        return agg_core_events_group
