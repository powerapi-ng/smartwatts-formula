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

import itertools
import logging
from collections import OrderedDict, defaultdict
from math import ldexp, fabs

from powerapi.handler import Handler
from powerapi.report import PowerReport, HWPCReport, FormulaReport
from sklearn.exceptions import NotFittedError

from smartwatts.model.power_model import PowerModel


class HwPCReportHandler(Handler):
    """
    HwPC reports handler.
    """

    def __init__(self, state):
        Handler.__init__(self, state)
        self.models = self._gen_models_dict()
        self.ticks = OrderedDict()

    def _gen_models_dict(self):
        """
        Generate and returns a layered container to store per-frequency power models
        :return: Initialized Ordered dict containing a power model for each frequency layer
        """
        return OrderedDict(
            (freq, PowerModel(freq, self.state.config.history_window_size)) for freq
            in self.state.config.cpu_topology.get_supported_frequencies())

    def _get_frequency_layer(self, frequency):
        """
        Find and returns the nearest frequency layer for the given frequency.
        :param frequency: CPU frequency
        :return: The nearest frequency layer for the given frequency
        """
        last_layer_freq = 0
        for current_layer_freq in self.models.keys():
            if frequency < current_layer_freq:
                return last_layer_freq
            last_layer_freq = current_layer_freq

        return last_layer_freq

    def compute_pkg_frequency(self, system_msr):
        """
        Compute the average package frequency.
        :param system_msr: MSR events group of System target
        :return: Average frequency of the Package
        """
        return (self.state.config.cpu_topology.get_base_frequency() * system_msr['APERF']) / system_msr['MPERF']

    def get_power_model(self, system_core):
        """
        Fetch the suitable power model for the current frequency.
        :param system_core: Core events group of System target
        :return: Power model to use for the current frequency
        """
        return self.models[self._get_frequency_layer(self.compute_pkg_frequency(system_core))]

    def handle(self, msg: HWPCReport):

        """
         Process a HWPC report and send the result(s) to a pusher actor.
         :param msg: Received message
        """
        logging.debug('received message: %s', msg)
        self.ticks.setdefault(msg.timestamp, {}).update({msg.target: msg})

        # Start to process the oldest tick only after receiving at least 5 ticks.
        # We wait before processing the ticks in order to mitigate the possible delay between the sensor/database.
        if len(self.ticks) > 5:
            power_reports, formula_reports = self._process_oldest_tick()
            for report in itertools.chain(power_reports, formula_reports):
                for name, pusher in self.state.pushers.items():
                    if isinstance(report, pusher.state.report_model):
                        pusher.send_data(report)
                        logging.debug('sent report: %s to %s', report, name)

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
        rapl_power = rapl[self.state.config.rapl_event]
        power_reports.append(
            self._gen_power_report(timestamp, 'rapl', self.state.config.rapl_event, 0.0, rapl_power, 1.0, {}))

        if not global_core:
            return power_reports, formula_reports

        # fetch power model to use
        try:
            pkg_frequency = self.compute_pkg_frequency(avg_msr)
            model = self.get_power_model(avg_msr)
        except ZeroDivisionError:
            return power_reports, formula_reports

        # compute Global target power report
        try:
            raw_global_power = model.compute_power_estimation(global_core)
            power_reports.append(
                self._gen_power_report(timestamp, 'global', model.hash, raw_global_power, raw_global_power, 1.0, {}))
        except NotFittedError:
            model.store_report_in_history(rapl_power, global_core)
            model.learn_power_model(self.state.config.min_samples_required, 0.0, self.state.config.cpu_topology.tdp)
            return power_reports, formula_reports

        # compute per-target power report
        for target_name, target_report in hwpc_reports.items():
            raw_target_power = model.compute_power_estimation(self._gen_core_events_group(target_report))
            target_power, target_ratio = model.cap_power_estimation(raw_target_power, raw_global_power)
            power_reports.append(
                self._gen_power_report(
                    timestamp,
                    target_name,
                    model.hash,
                    raw_target_power,
                    target_power,
                    target_ratio,
                    target_report.metadata)
            )

        # compute power model error from reference
        model_error = fabs(rapl_power - raw_global_power)

        # store global report
        model.store_report_in_history(rapl_power, global_core)

        # learn new power model if error exceeds the error threshold
        if model_error > self.state.config.error_threshold:
            model.learn_power_model(self.state.config.min_samples_required, 0.0, self.state.config.cpu_topology.tdp)

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
            'scope': self.state.config.scope.value,
            'socket': self.state.socket,
            'layer_frequency': model.frequency,
            'pkg_frequency': pkg_frequency,
            'samples': len(model.history),
            'id': model.id,
            'error': error,
            'intercept': model.model.intercept_,
            'coef': str(model.model.coef_)
        }
        return FormulaReport(timestamp, self.state.sensor, model.hash, metadata)

    def _gen_power_report(self, timestamp, target, formula, raw_power, power, ratio, metadata):
        """
        Generate a power report using the given parameters.
        :param timestamp: Timestamp of the measurements
        :param target: Target name
        :param formula: Formula identifier
        :param power: Power estimation
        :return: Power report filled with the given parameters
        """
        metadata.update({
            'scope': self.state.config.scope.value,
            'socket': self.state.socket,
            'formula': formula,
            'ratio': ratio,
            'predict': raw_power,
        })
        return PowerReport(timestamp, self.state.sensor, target, power, metadata)

    def _gen_rapl_events_group(self, system_report):
        """
        Generate an events group with the RAPL reference event converted in Watts for the current socket.
        :param system_report: The HWPC report of the System target
        :return: A dictionary containing the RAPL reference event with its value converted in Watts
        """
        cpu_events = next(iter(system_report.groups['rapl'][str(self.state.socket)].values()))
        energy = ldexp(cpu_events[self.state.config.rapl_event], -32) / (self.state.config.reports_frequency / 1000)
        return {self.state.config.rapl_event: energy}

    def _gen_msr_events_group(self, system_report):
        """
        Generate an events group with the average of the MSR counters for the current socket.
        :param system_report: The HWPC report of the System target
        :return: A dictionary containing the average of the MSR counters
        """
        msr_events_group = defaultdict(int)
        msr_events_count = defaultdict(int)
        for _, cpu_events in system_report.groups['msr'][str(self.state.socket)].items():
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
        for _, cpu_events in report.groups['core'][str(self.state.socket)].items():
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
