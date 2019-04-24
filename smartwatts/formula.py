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
from sklearn import linear_model

# make scikit-learn more silent
from sklearn.linear_model import Ridge

warnings.filterwarnings('ignore', category=LinAlgWarning)
warnings.filterwarnings('ignore', category=UserWarning)


class OutOfRangeFrequencyException(Exception):
    """
    This exception happens when an unsupported (too high) frequency is used in the formula.
    """
    pass


class PowerModelNotInitializedException(Exception):
    """
    This exception happens when a user try to compute a power estimation without having learned a power model.
    """
    pass


class SystemReportWrapper:
    """
    This wrapper stores the needed information for a System report and ease its usage when learning a power model.
    """

    def __init__(self, rapl: Dict[str, float], pcu: Dict[str, int], core: Dict[str, int]) -> None:
        self.rapl = rapl
        self.pcu = pcu
        self.core = core

    def X(self) -> List[int]:
        """
        Creates and return a list of events value from the PCU and Core events group.
        The elements are sorted by the name of the events.
        :return: List containing the PCU and Core events value sorted by event name.
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

    def __init__(self, frequency) -> None:
        self.frequency = frequency
        self.model: Union[Ridge, None] = None
        self.hash: str = 'uninitialized'
        self.reports: List[SystemReportWrapper] = []

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

    def store(self, rapl: Dict[str, float], pcu: Dict[str, int], system_core: Dict[str, int]) -> None:
        """
        Store the events group into the System reports list and learn a new power model.
        :param rapl: RAPL events group
        :param pcu: PCU events group
        :param system_core: Core events group of System target
        :return: Nothing
        """
        self.reports.append(SystemReportWrapper(rapl, pcu, system_core))

        if len(self.reports) > 3:
            self._learn()

    def compute_global_power_estimation(self, rapl: Dict[str, float], pcu: Dict[str, int], global_core: Dict[str, int]) -> float:
        """
        Compute the global power estimation using the power model.
        :param rapl: RAPL events group
        :param pcu: PCU events group
        :param global_core: Core events group of all target
        :return:
        """
        if not self.model:
            self.store(rapl, pcu, global_core)
            raise PowerModelNotInitializedException()

        report = SystemReportWrapper(rapl, pcu, global_core)
        return self.model.predict([report.X()])[0, 0]

    def compute_target_power_estimation(self, rapl: Dict[str, float], pcu: Dict[str, int], system_core: Dict[str, int], target_core: Dict[str, int]) -> (float, float):
        """
        Compute a power estimation for the given target.
        :param rapl: RAPL events group
        :param pcu: PCU events group
        :param system_core: Core events group of System target
        :param target_core: Core events group of any target
        :return: Power estimation for the given target
        :raise: PowerModelNotInitializedException when the power model is not initialized
        """
        if not self.model:
            self.store(rapl, pcu, system_core)
            raise PowerModelNotInitializedException()

        ref_power = next(iter(rapl.values()))
        system = SystemReportWrapper(rapl, pcu, system_core).X()
        target = SystemReportWrapper(rapl, pcu, target_core).X()

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

    def __init__(self) -> None:
        self.models = self._gen_models_dict(1000, 4200, 100)  # ONLY for microarchitectures newer than Sandy Bridge.

    @staticmethod
    def _gen_models_dict(freq_min: int, freq_max: int, freq_bclk: int) -> Dict[int, PowerModel]:
        """
        Generate and returns a layered container to store per-frequency power models.
        :param freq_min: Minimum frequency in Hz
        :param freq_max: Maximum frequency in Hz
        :param freq_bclk: Base clock frequency in Hz
        :return: Initialized Ordered dict containing a power model for each frequency layer.
        """
        return OrderedDict((frequency, PowerModel(frequency)) for frequency in range(freq_min, freq_max + 1, freq_bclk))

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
        return (2100 * system_msr['APERF']) / system_msr['MPERF']  # TODO: the base frequency should not be hardcoded

    def get_power_model(self, system_core: Dict[str, int]) -> PowerModel:
        """
        Fetch the suitable power model for the current frequency.
        :param system_core: Core events group of System target
        :return: Power model to use for the current frequency
        """
        return self.models[self._get_frequency_layer(self._compute_pkg_frequency(system_core))]
