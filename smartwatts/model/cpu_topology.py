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

class CPUTopology:
    """
    This class stores the necessary information about the CPU topology.
    """

    def __init__(self, tdp, freq_bclk, ratio_min, ratio_base, ratio_max):
        """
        Create a new CPU topology object.
        :param tdp: TDP of the CPU in Watt
        :param freq_bclk: Base clock in MHz
        :param ratio_min: Maximum efficiency ratio
        :param ratio_base: Base frequency ratio
        :param ratio_max: Maximum frequency ratio (with Turbo-Boost)
        """
        self.tdp = tdp
        self.freq_bclk = freq_bclk
        self.ratio_min = ratio_min
        self.ratio_base = ratio_base
        self.ratio_max = ratio_max

    def get_min_frequency(self):
        """
        Compute and return the CPU max efficiency frequency.
        :return: The CPU max efficiency frequency in MHz
        """
        return self.freq_bclk * self.ratio_min

    def get_base_frequency(self):
        """
        Compute and return the CPU base frequency.
        :return: The CPU base frequency in MHz
        """
        return self.freq_bclk * self.ratio_base

    def get_max_frequency(self):
        """
        Compute and return the CPU maximum frequency. (Turbo-Boost included)
        :return: The CPU maximum frequency in MHz
        """
        return self.freq_bclk * self.ratio_max

    def get_supported_frequencies(self):
        """
        Compute the supported frequencies for this CPU.
        :return: A list of supported frequencies in MHz
        """
        return list(range(self.get_min_frequency(), self.get_max_frequency() + 1, self.freq_bclk))
