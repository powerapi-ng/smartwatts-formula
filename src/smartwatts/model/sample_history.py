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

from collections import deque
from statistics import median, mean
from typing import List


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
        self.events_values = deque(maxlen=max_length)
        self.power_values = deque(maxlen=max_length)

    def __len__(self) -> int:
        """
        Compute the length of the history.
        :return: Length of the history
        """
        return len(self.events_values)

    def store_report(self, power_reference: float, events_value: List[float]) -> None:
        """
        Append a report to the report's history.
        :param events_value: List of raw events value
        :param power_reference: Power reference corresponding to the events value
        """
        self.events_values.append(events_value)
        self.power_values.append(power_reference)


class ErrorHistory:
    """
    This class stores the error history used to trigger the learning of a new power model.
    """

    def __init__(self, max_length: int):
        """
        Initialize a new error history container.
        :param max_length: Maximum amount of samples to keep before overriding the oldest sample at insertion
        """
        self.max_length = max_length
        self.error_values = deque(maxlen=max_length)

    def __len__(self) -> int:
        """
        Compute the length of the history.
        :return: Length of the history
        """
        return len(self.error_values)

    def store_error(self, error_value: float) -> None:
        """
        Append a report to the report's history.
        :param error_value: Power reference corresponding to the events value
        """
        self.error_values.append(error_value)

    def clear(self) -> None:
        """
        Clear the error history.
        """
        self.error_values.clear()

    def compute_error(self, method: str = 'median') -> float:
        """
        Compute the error from the history.
        :param method: Method to use to compute the error (median or mean)
        :return: Error value
        """
        if method == 'median':
            return median(self.error_values)

        if method == 'mean':
            return mean(self.error_values)

        raise ValueError(f'Unknown method {method}')
