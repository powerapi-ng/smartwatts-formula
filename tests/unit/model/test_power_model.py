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

from smartwatts.model import PowerModel


def test_store_power_reports_in_history():
    """
    Test that the power report is correctly stored in the reports history of the model.
    """
    model = PowerModel(0, 3)

    model.store_report_in_history(0.0, {'A': 1.0, 'B': 2.0})
    model.store_report_in_history(0.1, {'A': 1.1, 'B': 2.1})
    model.store_report_in_history(0.2, {'A': 1.2, 'B': 2.2})
    assert list(model.samples_history.events_values) == [[1.0, 2.0], [1.1, 2.1], [1.2, 2.2]]
    assert list(model.samples_history.power_values) == [0.0, 0.1, 0.2]


def test_cap_power_estimation_zero_target_and_total_power():
    """
    Test that capping a zero target and global power estimation with a zero intercept returns 0.
    """
    model = PowerModel(0, 0)
    model.model.intercept_ = 0.0

    power, ratio = model.cap_power_estimation(0.0, 0.0)
    assert power == 0.0
    assert ratio == 0.0


def test_cap_power_estimation_zero_target_and_total_power_with_nonzero_intercept():
    """
    Test that capping a zero target and global power estimation with a non-zero intercept returns 0.
    """
    model = PowerModel(0, 0)
    model.model.intercept_ = 10.0

    power, ratio = model.cap_power_estimation(0.0, 0.0)
    assert power == 0.0
    assert ratio == 0.0


def test_cap_power_estimation_target_half_total_power():
    """
    Test that capping the target power estimation when the target power is half of the global power is working.
    """
    model = PowerModel(0, 0)
    model.model.intercept_ = 0.0

    power, ratio = model.cap_power_estimation(50.0, 100.0)
    assert power == 50.0
    assert ratio == 0.5


def test_cap_power_estimation_total_equal_target_power():
    """
    Test that capping the power estimation of the target when it is equal to the global is working.
    """
    model = PowerModel(0, 0)
    model.model.intercept_ = 0.0

    power, ratio = model.cap_power_estimation(100.0, 100.0)
    assert power == 100.0
    assert ratio == 1.0


def test_cap_power_estimation_target_power_double_of_total_power():
    """
    Test that capping the power estimation of the target when it is double of the global power is working.
    """
    model = PowerModel(0, 0)
    model.model.intercept_ = 0.0

    power, ratio = model.cap_power_estimation(200.0, 100.0)
    assert power == 200.0
    assert ratio == 2.0


def test_cap_power_estimation_negative_target_power():
    """
    Test that capping a negative target power estimation returns 0.
    """
    model = PowerModel(0, 0)
    model.model.intercept_ = 0.0

    power, ratio = model.cap_power_estimation(-200.0, 100.0)
    assert power == 0.0
    assert ratio == 0.0


def test_cap_power_estimation_when_intercept_greater_than_total_power():
    """
    Test that capping the power estimation of the target when the intercept is greater than the global power returns 0.
    """
    model = PowerModel(0, 0)
    model.model.intercept_ = 200.0

    power, ratio = model.cap_power_estimation(100.0, 100.0)
    assert power == 0.0
    assert ratio == 0.0


def test_cap_power_estimation_with_nonzero_intercept():
    """
    Test that capping the power estimation of the target with a non-zero intercept is working.
    """
    model = PowerModel(0, 0)
    model.model.intercept_ = 10.0

    power, ratio = model.cap_power_estimation(20.0, 110.0)
    assert power == 10.0 + (ratio * model.model.intercept_)
    assert ratio == 0.1
