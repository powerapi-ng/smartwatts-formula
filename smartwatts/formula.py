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

import hashlib
import pickle
import warnings
from collections import OrderedDict
from typing import List, Dict, Union

from scipy.linalg import LinAlgWarning
from sklearn.linear_model import Ridge

from smartwatts.topology import CPUTopology

# make scikit-learn more silent
warnings.filterwarnings('ignore', category=LinAlgWarning)
warnings.filterwarnings('ignore', category=UserWarning)


class PowerModelNotInitializedException(Exception):
    """
    This exception happens when a user try to compute a power estimation without having learned a power model.
    """
    pass


class NotEnoughReportsInHistoryException(Exception):
    """
    This exception happens when a user try to learn a power model without having enough reports in history.
    """
    pass


class History:
    """
    This class stores the reports history to use when learning a new power model.
    """

    def __init__(self) -> None:
        """
        Initialize a new reports history container.
        """
        self.X: List[List[int]] = []
        self.y: List[float] = []

    def __len__(self) -> int:
        """
        Compute the length of the history.
        :return: Length of the history
        """
        return len(self.X)

    def store_report(self, power_reference: float, events_value: List[int]) -> None:
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

    def __init__(self, frequency: int) -> None:
        """
        Initialize a new power model.
        :param frequency: Frequency of the power model
        """
        self.frequency = frequency
        self.model: Union[Ridge, None] = None
        self.hash: str = 'uninitialized'
        self.history: History = History()
        self.id = 0

    def learn_power_model(self) -> None:
        """
        Learn a new power model using the stored reports and update the formula hash.
        :raise: NotEnoughReportsInHistoryException when trying to learn without enough previous data
        """
        if len(self.history) < 3:
            return

        self.model = Ridge().fit(self.history.X, self.history.y)
        self.hash = hashlib.blake2b(pickle.dumps(self.model), digest_size=20).hexdigest()
        self.id += 1

    @staticmethod
    def _extract_events_value(events: Dict[str, int]) -> List[int]:
        """
        Creates and return a list of events value from the events group.
        :param events: Events group
        :return: List containing the events value sorted by event name
        """
        return [value for _, value in sorted(events.items())]

    def store_report_in_history(self, power_reference: float, events: Dict[str, int]) -> None:
        """
        Store the events group into the System reports list and learn a new power model.
        :param power_reference: Power reference (in Watt)
        :param events: Events value
        """
        self.history.store_report(power_reference, self._extract_events_value(events))

    def compute_power_estimation(self, events: Dict[str, int]) -> float:
        """
        Compute a power estimation from the events value using the power model.
        :param events: Events value
        :raise: PowerModelNotInitializedException when haven't been initialized
        :return: Power estimation for the given events value
        """
        if not self.model:
            raise PowerModelNotInitializedException()

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
        power = global_power * ratio if ratio > 0.0 else 0.0
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


class SmartWattsFormula:
    """
    This formula compute per-target power estimations using hardware performance counters.
    """

    def __init__(self, cpu_topology: CPUTopology) -> None:
        """
        Initialize a new formula.
        :param cpu_topology: CPU topology to use
        """
        self.cpu_topology = cpu_topology
        self.models = self._gen_models_dict()

    def _gen_models_dict(self) -> Dict[int, PowerModel]:
        """
        Generate and returns a layered container to store per-frequency power models.
        :return: Initialized Ordered dict containing a power model for each frequency layer
        """
        return OrderedDict((freq, PowerModel(freq)) for freq in self.cpu_topology.get_supported_frequencies())

    def _get_frequency_layer(self, frequency: float) -> int:
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

    def compute_pkg_frequency(self, system_msr: Dict[str, int]) -> float:
        """
        Compute the average package frequency.
        :param msr: MSR events group of System target
        :return: Average frequency of the Package
        """
        return (self.cpu_topology.get_base_frequency() * system_msr['APERF']) / system_msr['MPERF']

    def get_power_model(self, system_core: Dict[str, int]) -> PowerModel:
        """
        Fetch the suitable power model for the current frequency.
        :param system_core: Core events group of System target
        :return: Power model to use for the current frequency
        """
        return self.models[self._get_frequency_layer(self.compute_pkg_frequency(system_core))]
