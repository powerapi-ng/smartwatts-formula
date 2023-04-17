# Copyright (c) 2023, INRIA
# Copyright (c) 2023, University of Lille
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

from smartwatts.model import CPUTopology


def test_cpu_topology_amd_epyc_7351():
    """
    Test the CPUTopology class with an AMD EPYC 7351 CPU configuration.
    https://www.amd.com/en/support/cpu/amd-epyc/amd-epyc-7001-series/amd-epyc-7351
    """
    cpu_topology = CPUTopology(155, 100.0, 12, 24, 29)
    assert cpu_topology.get_min_frequency() == 1200.0
    assert cpu_topology.get_base_frequency() == 2400.0
    assert cpu_topology.get_max_frequency() == 2900.0
    assert cpu_topology.get_supported_frequencies() == [ratio * 100.0 for ratio in range(12, 29 + 1)]


def test_cpu_topology_intel_xeon_gold_5220():
    """
    Test the CPUTopology class with an Intel Xeon Gold 5220 CPU configuration.
    https://www.intel.com/content/www/us/en/products/sku/193388/intel-xeon-gold-5220-processor-24-75m-cache-2-20-ghz/
    """
    cpu_topology = CPUTopology(125, 100.0, 10, 22, 39)
    assert cpu_topology.get_min_frequency() == 1000.0
    assert cpu_topology.get_base_frequency() == 2200.0
    assert cpu_topology.get_max_frequency() == 3900.0
    assert cpu_topology.get_supported_frequencies() == [ratio * 100.0 for ratio in range(10, 39 + 1)]


def test_cpu_topology_with_133mhz_base_clock():
    """
    Test the CPUTopology class with a base clock of 133MHz.
    """
    cpu_topology = CPUTopology(0, 133.0, 10, 20, 30)
    assert cpu_topology.get_min_frequency() == 1330.0
    assert cpu_topology.get_base_frequency() == 2660.0
    assert cpu_topology.get_max_frequency() == 3990.0
    assert cpu_topology.get_supported_frequencies() == [ratio * 133.0 for ratio in range(10, 30 + 1)]
