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

from typing import List


class CpuTopology:
    """
    This class stores the necessary information about the CPU topology.
    """

    def __init__(self, freq_bclk: int, freq_min: int, freq_base: int, freq_max: int) -> None:
        """
        Create a new CPU topology object.
        :param freq_bclk: Base clock in MHz
        :param freq_min: Minimal frequency (MEF) in kHz
        :param freq_base: Base frequency in kHz
        :param freq_max: Maximum frequency in kHz
        """
        self.freq_bclk = freq_bclk
        self.freq_min = freq_min
        self.freq_base = freq_base
        self.freq_max = freq_max

    def get_supported_frequencies(self) -> List[int]:
        """
        Compute the available frequencies for this CPU.
        :return: A list of supported frequencies in kHz
        """
        return [frequency for frequency in range(self.freq_min, self.freq_max + 1, self.freq_bclk)]
