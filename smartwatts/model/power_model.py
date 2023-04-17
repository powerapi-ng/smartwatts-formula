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

from collections import deque
from hashlib import sha1
from pickle import dumps
from typing import Dict, List

from sklearn.linear_model import ElasticNet


class ReportHistory:
    """
    This class stores the reports history to use when learning a new power model.
    """

    def __init__(self, max_length: int):
        """
        Initialize a new reports history container.
        :param max_length: Maximum amount of samples to keep before overriding the oldest sample at insertion
        """
        self.max_length = max_length
        self.X = deque(maxlen=max_length)
        self.y = deque(maxlen=max_length)

    def __len__(self) -> int:
        """
        Compute the length of the history.
        :return: Length of the history
        """
        return len(self.X)

    def store_report(self, power_reference: float, events_value: List[float]) -> None:
        """
        Append a report to the report's history.
        :param events_value: List of raw events value
        :param power_reference: Power reference corresponding to the events value
        """
        self.X.append(events_value)
        self.y.append(power_reference)


class PowerModel:
    """
    This Power model compute the power estimations and handle the learning of a new model when needed.
    """

    def __init__(self, frequency: float, history_window_size: int):
        """
        Initialize a new power model.
        :param frequency: Frequency of the power model
        :param history_window_size: Size of the history window used to keep samples to learn from
        """
        self.frequency = frequency
        self.model = ElasticNet()
        self.hash = 'uninitialized'
        self.history = ReportHistory(history_window_size)
        self.id = 0

    def learn_power_model(self, min_samples: int, min_intercept: float, max_intercept: float) -> None:
        """
        Learn a new power model using the stored reports and update the formula id/hash.
        :param min_samples: Minimum amount of samples required to learn the power model
        :param min_intercept: Minimum value allowed for the intercept of the model
        :param max_intercept: Maximum value allowed for the intercept of the model
        """
        if len(self.history) < min_samples:
            return

        fit_intercept = len(self.history) == self.history.max_length
        model = ElasticNet(fit_intercept=fit_intercept, positive=True)
        model.fit(self.history.X, self.history.y)

        # Discard the new model when the intercept is not in specified range
        if not min_intercept <= model.intercept_ < max_intercept:
            return

        self.model = model
        self.hash = sha1(dumps(self.model)).hexdigest()
        self.id += 1

    @staticmethod
    def _extract_events_value(events: Dict[str, float]) -> List[float]:
        """
        Creates and return a list of events value from the events group.
        :param events: Events group
        :return: List containing the events value sorted by event name
        """
        return [value for _, value in sorted(events.items())]

    def store_report_in_history(self, power_reference: float, events: Dict[str, float]) -> None:
        """
        Store the events group into the System reports list and learn a new power model.
        :param power_reference: Power reference (in Watt)
        :param events: Events value
        """
        self.history.store_report(power_reference, self._extract_events_value(events))

    def compute_power_estimation(self, events: Dict[str, float]) -> float:
        """
        Compute a power estimation from the events value using the power model.
        :param events: Events value
        :raise: NotFittedError when the model haven't been fitted
        :return: Power estimation for the given events value
        """
        return self.model.predict([self._extract_events_value(events)])[0]

    def cap_power_estimation(self, raw_target_power: float, raw_global_power: float) -> (float, float):
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

    def apply_intercept_share(self, target_power: float, target_ratio: float) -> float:
        """
        Apply the target's share of intercept from its ratio from the global power consumption.
        :param target_power: Target power estimation (in Watt)
        :param target_ratio: Target ratio over the global power consumption
        :return: Target power estimation including intercept (in Watt) and ratio over global power consumption
        """
        intercept = target_ratio * self.model.intercept_
        return target_power + intercept
