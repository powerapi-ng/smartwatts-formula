# BSD 3-Clause License
#
# Copyright (c) 2023, Inria
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

from typing import List

from .sample_history import ReportHistory, ErrorHistory
from .power_model import PowerModel


class FrequencyLayer:
    """
    Frequency layer of the CPU.
    """

    def __init__(self, frequency: int, min_samples: int, samples_window_size: int, error_window_size: int) -> None:
        """
        Initialize a new frequency layer.
        :param min_samples: Minimum amount of samples required before trying to learn a power model
        :param samples_window_size: Size of the samples history window used to keep samples to learn from
        :param error_window_size: Size of the error history window used to keep errors of the model
        """
        self.model = PowerModel(frequency, min_samples)
        self.samples_history = ReportHistory(samples_window_size)
        self.error_history = ErrorHistory(error_window_size)

    def update_power_model(self, min_intercept: float, max_intercept: float) -> None:
        """
        Learn a new power model using the sample's history.
        :param min_intercept: Minimum intercept value allowed for the model
        :param max_intercept: Maximum intercept value allowed for the model
        """
        self.model.learn_power_model(self.samples_history, min_intercept, max_intercept)
        self.error_history.clear()

    def store_sample_in_history(self, power_reference: float, events_value: List[float]) -> None:
        """
        Append a sample to the history.
        :param power_reference: Power reference (RAPL) of the machine
        :param events_value: Events value (Hardware Performance Counters) of the target
        """
        self.samples_history.store_report(power_reference, events_value)

    def store_error_in_history(self, error: float) -> None:
        """
        Append an error to the history.
        :param error: Power model error
        """
        self.error_history.store_error(error)
