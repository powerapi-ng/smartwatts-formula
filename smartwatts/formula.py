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


class ReportWrapper:
    """
    This wrapper stores the needed information for a System report and ease its usage when learning a power model.
    """

    def __init__(self, rapl: Dict[str, float], core: Dict[str, int]) -> None:
        self.rapl = rapl
        self.core = core

    def X(self) -> List[int]:
        """
        Creates and return a list of events value from the Core events group.
        :return: List containing the Core events value sorted by event name.
        """
        return [v for _, v in sorted(self.core.items())]

    def y(self) -> List[float]:
        """
        Creates and return a list of events value from the RAPL events group.
        :return: List containing the RAPL events value.
        """
        return [v for _, v in sorted(self.rapl.items())]


class PowerModel:
    """
    This Power model compute the power estimations and handle the learning of a new model when needed.
    """

    def __init__(self, frequency: int) -> None:
        self.frequency = frequency
        self.model: Union[Ridge, None] = None
        self.hash: str = 'uninitialized'
        self.reports: List[ReportWrapper] = []

    def _learn(self) -> None:
        """
        Learn a new power model using the stored reports and update the formula hash.
        :return: Nothing
        """
        X = []
        y = []
        for report in self.reports:
            X.append(report.X())
            y.append(report.y())

        self.model = Ridge().fit(X, y)
        self.hash = hashlib.blake2b(pickle.dumps(self.model), digest_size=20).hexdigest()

    def store(self, rapl: Dict[str, float], global_core: Dict[str, int]) -> None:
        """
        Store the events group into the System reports list and learn a new power model.
        :param rapl: RAPL events group
        :param global_core: Core events group of all targets
        :return: Nothing
        """
        self.reports.append(ReportWrapper(rapl, global_core))

        if len(self.reports) > 3:
            self._learn()

    def compute_global_power_estimation(self, rapl: Dict[str, float], global_core: Dict[str, int]) -> float:
        """
        Compute the global power estimation using the power model.
        :param rapl: RAPL events group
        :param global_core: Core events group of all targets
        :return:
        """
        if not self.model:
            self.store(rapl, global_core)
            raise PowerModelNotInitializedException()

        report = ReportWrapper(rapl, global_core)
        return self.model.predict([report.X()])[0, 0]

    def compute_target_power_estimation(self, rapl: Dict[str, float], global_core: Dict[str, int], target_core: Dict[str, int]) -> (float, float):
        """
        Compute a power estimation for the given target.
        :param rapl: RAPL events group
        :param global_core: Core events group of all targets
        :param target_core: Core events group of any target
        :return: Power estimation for the given target
        :raise: PowerModelNotInitializedException when the power model is not initialized
        """
        if not self.model:
            self.store(rapl, global_core)
            raise PowerModelNotInitializedException()

        ref_power = next(iter(rapl.values()))
        system = ReportWrapper(rapl, global_core).X()
        target = ReportWrapper(rapl, target_core).X()

        coefs = next(iter(self.model.coef_))
        sum_coefs = sum(coefs)

        ratio = 0.0
        for index, coef in enumerate(coefs):
            try:
                ratio += (coef / sum_coefs) * (target[index] / system[index])
            except ZeroDivisionError:
                pass

        target_power = ref_power * ratio
        if target_power < 0.0:
            return 0.0, 0.0

        return target_power, ratio


class SmartWattsFormula:
    """
    This formula compute per-target power estimations using hardware performance counters.
    """

    def __init__(self, cpu_topology: CPUTopology) -> None:
        self.cpu_topology = cpu_topology
        self.models = self._gen_models_dict()

    def _gen_models_dict(self) -> Dict[int, PowerModel]:
        """
        Generate and returns a layered container to store per-frequency power models.
        :return: Initialized Ordered dict containing a power model for each frequency layer.
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

    def _compute_pkg_frequency(self, system_msr: Dict[str, int]) -> float:
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
        return self.models[self._get_frequency_layer(self._compute_pkg_frequency(system_core))]
