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
from collections import OrderedDict, defaultdict
from datetime import datetime
from math import ldexp, fabs
from typing import Dict, List

from powerapi.handler import Handler
from powerapi.message import UnknowMessageTypeException
from powerapi.report import HWPCReport, PowerReport
from powerapi.report.formula_report import FormulaReport

from smartwatts.context import SmartWattsFormulaState
from smartwatts.formula import SmartWattsFormula, PowerModelNotInitializedException, PowerModel


class ReportHandler(Handler):
    """
    This reports handler process the HWPC reports to compute a per-target power estimation.
    """

    def __init__(self, state: SmartWattsFormulaState):
        """
        Initialize a new report handler.
        :param state: State of the actor
        """
        Handler.__init__(self, state)
        self.state = state
        self.ticks = OrderedDict()
        self.formula = SmartWattsFormula(state.config.cpu_topology)

    def _gen_rapl_events_group(self, system_report: HWPCReport) -> Dict[str, float]:
        """
        Generate an events group with the RAPL reference event converted in Watts for the current socket.
        :param system_report: The HWPC report of the System target
        :return: A dictionary containing the RAPL reference event with its value converted in Watts
        """
        cpu_events = next(iter(system_report.groups['rapl'][self.state.socket].values()))
        energy = ldexp(cpu_events[self.state.config.rapl_event], -32) / (self.state.config.reports_frequency / 1000)
        return {self.state.config.rapl_event: energy}

    def _gen_msr_events_group(self, system_report: HWPCReport) -> Dict[str, int]:
        """
        Generate an events group with the average of the MSR counters for the current socket.
        :param system_report: The HWPC report of the System target
        :return: A dictionary containing the average of the MSR counters
        """
        msr_events_group = defaultdict(int)
        msr_events_count = defaultdict(int)
        for _, cpu_events in system_report.groups['msr'][self.state.socket].items():
            for event_name, event_value in {k: v for k, v in cpu_events.items() if not k.startswith('time_')}.items():
                msr_events_group[event_name] += event_value
                msr_events_count[event_name] += 1

        return {k: (v / msr_events_count[k]) for k, v in msr_events_group.items()}

    def _gen_core_events_group(self, report: HWPCReport) -> Dict[str, int]:
        """
        Generate an events group with Core events for the current socket.
        The events value are the sum of the value for each CPU.
        :param report: The HWPC report of any target
        :return: A dictionary containing the Core events of the current socket
        """
        core_events_group = defaultdict(int)
        for _, cpu_events in report.groups['core'][self.state.socket].items():
            for event_name, event_value in {k: v for k, v in cpu_events.items() if not k.startswith('time_')}.items():
                core_events_group[event_name] += event_value

        return core_events_group

    def _gen_agg_core_report_from_running_targets(self, targets_report: Dict[str, HWPCReport]) -> Dict[str, int]:
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

    def _gen_power_report(self, timestamp: datetime, target: str, formula: str, raw_power: float, power: float, ratio: float) -> PowerReport:
        """
        Generate a power report using the given parameters.
        :param timestamp: Timestamp of the measurements
        :param target: Target name
        :param formula: Formula identifier
        :param power: Power estimation
        :return: Power report filled with the given parameters
        """
        metadata = {
            'scope': self.state.config.scope.value,
            'socket': self.state.socket,
            'formula': formula,
            'ratio': ratio,
            'predict': raw_power,
        }
        return PowerReport(timestamp, self.state.sensor, target, power, metadata)

    def _gen_formula_report(self, timestamp: datetime, pkg_frequency: float, model: PowerModel, error: float) -> FormulaReport:
        """
        Generate a formula report using the given parameters.
        :param timestamp: Timestamp of the measurements
        :param pkg_frequency: Package average frequency
        :param model: Power model used for the estimation
        :param error: Error rate of the model
        :return: Formula report filled with the given parameters
        """
        metadata = {
            'scope': self.state.config.scope.value,
            'socket': self.state.socket,
            'layer_frequency': model.frequency,
            'pkg_frequency': pkg_frequency,
            'samples': len(model.history),
            'id': model.id,
            'error': error,
            'intercept': model.model.intercept_
        }
        return FormulaReport(timestamp, self.state.sensor, model.hash, metadata)

    def _process_oldest_tick(self) -> (List[PowerReport], List[FormulaReport]):
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
        rapl_power = rapl[self.state.config.rapl_event]
        power_reports.append(self._gen_power_report(timestamp, 'rapl', self.state.config.rapl_event, rapl_power, rapl_power, 1.0))

        # fetch power model to use
        pkg_frequency = self.formula.compute_pkg_frequency(avg_msr)
        model = self.formula.get_power_model(avg_msr)

        # compute Global target power report
        try:
            raw_global_power = model.compute_power_estimation(global_core)
            power_reports.append(self._gen_power_report(timestamp, 'global', model.hash, raw_global_power, raw_global_power, 1.0))
        except PowerModelNotInitializedException:
            model.store_report_in_history(rapl_power, global_core)
            model.learn_power_model()
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

        # store Global report if the power model error exceeds the error threshold
        if model_error > self.state.config.error_threshold:
            model.store_report_in_history(rapl_power, global_core)
            model.learn_power_model()

        # store information about the power model used for this tick
        formula_reports.append(self._gen_formula_report(timestamp, pkg_frequency, model, model_error))

        return power_reports, formula_reports

    def _process_report(self, report) -> None:
        """
        Process the received report and trigger the processing of the old ticks.
        :param report: HWPC report of a target
        """

        # store the received report into the tick's bucket
        self.ticks.setdefault(report.timestamp, {}).update({report.target: report})

        # start to process the oldest tick only after receiving at least 5 ticks.
        # we wait before processing the ticks in order to mitigate the possible delay of the sensor/database.
        if len(self.ticks) > 5:
            power_reports, formula_reports = self._process_oldest_tick()

            for report in power_reports + formula_reports:
                for _, pusher in self.state.pushers.items():
                    if isinstance(report, pusher.state.report_model.get_type()):
                        pusher.send_data(report)

    def handle(self, msg):
        """
        Process a report and send the result(s) to a pusher actor.
        :param msg: Received message
        :param state: Current actor state
        :return: New actor state
        :raise: UnknowMessageTypeException when the given message is not an HWPCReport
        """
        if not isinstance(msg, HWPCReport):
            raise UnknowMessageTypeException(type(msg))

        self._process_report(msg)
