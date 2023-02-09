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
from collections import deque, OrderedDict, defaultdict
from hashlib import sha1
from math import ldexp, fabs
from pickle import dumps

from powerapi.formula import FormulaPoisonPillMessageHandler
from powerapi.formula.abstract_cpu_dram_formula import AbstractCpuDramFormulaState
from powerapi.handler import Handler
from powerapi.report import PowerReport, HWPCReport
from sklearn.exceptions import NotFittedError
from sklearn.linear_model import ElasticNet as Regression

from smartwatts.report import FormulaReport


class History:
    """
    This class stores the reports history to use when learning a new power model.
    """

    def __init__(self, max_length):
        """
        Initialize a new reports history container.
        :param max_length: Maximum amount of samples to keep before overriding the oldest sample at insertion
        """
        self.max_length = max_length
        self.X = deque(maxlen=max_length)
        self.y = deque(maxlen=max_length)

    def __len__(self):
        """
        Compute the length of the history.
        :return: Length of the history
        """
        return len(self.X)

    def store_report(self, power_reference, events_value):
        """
        Append a report to the reports history.
        :param events_value: List of raw events value
        :param power_reference: Power reference corresponding to the events value
        """
        self.X.append(events_value)
        self.y.append(power_reference)


class PowerModel:
    """
    This Power model compute the power estimations and handle the learning of a new model when needed.
    """

    def __init__(self, frequency, history_window_size):
        """
        Initialize a new power model.
        :param frequency: Frequency of the power model
        :param history_window_size: Size of the history window used to keep samples to learn from
        """
        self.frequency = frequency
        self.model = Regression()
        self.hash = 'uninitialized'
        self.history = History(history_window_size)
        self.id = 0

    def learn_power_model(self, min_samples, min_intercept, max_intercept):
        """
        Learn a new power model using the stored reports and update the formula id/hash.
        :param min_samples: Minimum amount of samples required to learn the power model
        :param min_intercept: Minimum value allowed for the intercept of the model
        :param max_intercept: Maximum value allowed for the intercept of the model
        """
        if len(self.history) < min_samples:
            return

        fit_intercept = len(self.history) == self.history.max_length
        model = Regression(fit_intercept=fit_intercept, positive=True).fit(self.history.X, self.history.y)

        # Discard the new model when the intercept is not in specified range
        if not min_intercept <= model.intercept_ < max_intercept:
            return

        self.model = model
        self.hash = sha1(dumps(self.model)).hexdigest()
        self.id += 1

    @staticmethod
    def _extract_events_value(events):
        """
        Creates and return a list of events value from the events group.
        :param events: Events group
        :return: List containing the events value sorted by event name
        """
        return [value for _, value in sorted(events.items())]

    def store_report_in_history(self, power_reference, events):
        """
        Store the events group into the System reports list and learn a new power model.
        :param power_reference: Power reference (in Watt)
        :param events: Events value
        """
        self.history.store_report(power_reference, self._extract_events_value(events))

    def compute_power_estimation(self, events):
        """
        Compute a power estimation from the events value using the power model.
        :param events: Events value
        :raise: NotFittedError when the model haven't been fitted
        :return: Power estimation for the given events value
        """
        return self.model.predict([self._extract_events_value(events)])[0]

    def cap_power_estimation(self, raw_target_power, raw_global_power):
        """
        Cap target's power estimation to the global power estimation.
        :param raw_target_power: Target power estimation from the power model (in Watt)
        :param raw_global_power: Global power estimation from the power model (in Watt)
        :return: Capped power estimation (in Watt) with its ratio over global power consumption
        """
        target_power = raw_target_power - self.model.intercept_
        global_power = raw_global_power - self.model.intercept_

        ratio = target_power / global_power if global_power > 0.0 and target_power > 0.0 else 0.0
        power = target_power if target_power > 0.0 else 0.0
        return power, ratio

    def apply_intercept_share(self, target_power, target_ratio):
        """
        Apply the target's share of intercept from its ratio from the global power consumption.
        :param target_power: Target power estimation (in Watt)
        :param target_ratio: Target ratio over the global power consumption
        :return: Target power estimation including intercept (in Watt) and ratio over global power consumption
        """
        intercept = target_ratio * self.model.intercept_
        return target_power + intercept


class ReportHandler(Handler):
    """
    Handler behaviour for HWPC Reports
    """

    def __init__(self, state: AbstractCpuDramFormulaState):
        Handler.__init__(self, state=state)
        self.models = self._gen_models_dict()

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
        :return: Nearest frequency layer for the given frequency
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

    def handle(self, message: HWPCReport):

        """
         Process a HWPC report and send the result(s) to a pusher actor.
         :param message: Received message
        """
        self.state.actor.logger.debug('received message ' + str(message))
        self.state.ticks.setdefault(message.timestamp, {}).update({message.target: message})

        # start to process the oldest tick only after receiving at least 5 ticks.
        # we wait before processing the ticks in order to mitigate the possible delay of the sensor/database.
        if self.state.config.real_time_mode:
            if len(self.state.ticks) > 2:
                power_reports, formula_reports = self._process_oldest_tick()
                for report in power_reports:
                    for name, pusher in self.state.pushers.items():
                        pusher.send_data(report)
                        self.state.actor.logger.debug('send ' + str(report) + ' to ' + name)
                for report in formula_reports:
                    for name, pusher in self.state.formula_pushers.items():
                        pusher.send_data(report)
                        self.state.actor.logger.debug('send ' + str(report) + ' to ' + name)

        else:
            if len(self.state.ticks) > 5:
                power_reports, formula_reports = self._process_oldest_tick()
                for report in power_reports:
                    for name, pusher in self.state.pushers.items():
                        pusher.send_data(report)
                        self.state.actor.logger.debug('send ' + str(report) + ' to ' + name)
                for report in formula_reports:
                    for name, pusher in self.state.formula_pushers.items():
                        pusher.send_data(report)
                        self.state.actor.logger.debug('send ' + str(report) + ' to ' + name)

    def _process_oldest_tick(self):
        """
        Process the oldest tick stored in the stack and generate power reports for the running target(s).
        :return: Power reports of the running target(s)
        """
        timestamp, hwpc_reports = self.state.ticks.popitem(last=False)

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
            target_core = self._gen_core_events_group(target_report)
            raw_target_power = model.compute_power_estimation(target_core)
            target_power, target_ratio = model.cap_power_estimation(raw_target_power, raw_global_power)
            target_power = model.apply_intercept_share(target_power, target_ratio)
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


class SmartWattsFormulaPoisonPillMessageHandler(FormulaPoisonPillMessageHandler):
    """
    Smartwatts Handler for dealing with PoisonPillMessage
    """

    def teardown(self, soft=False):
        FormulaPoisonPillMessageHandler.teardown(self, soft=soft)
        for pusher in self.state.formula_pushers:
            pusher.socket_interface.close()
