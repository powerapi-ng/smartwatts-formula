# BSD 3-Clause License
#
# Copyright (c) 2022, Inria
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

from powerapi.cli import ConfigValidator

from smartwatts.exceptions import InvalidConfigurationParameterException


class SmartWattsConfigValidator(ConfigValidator):
    """
    Class used that check the config extracted and verify it conforms to constraints
    """

    @staticmethod
    def validate(config: dict):

        ConfigValidator.validate(config)

        if config['disable-cpu-formula'] and config['disable-dram-formula']:
            raise InvalidConfigurationParameterException('At least one of the two formula scope must be enabled')

        if config['cpu-tdp'] < 0 or config['cpu-base-clock'] < 0 or config['cpu-base-freq'] < 0:
            raise InvalidConfigurationParameterException('CPU topology parameters (tdp/frequencies) must be positive')

        if config['cpu-error-threshold'] < 0 or config['dram-error-threshold'] < 0:
            raise InvalidConfigurationParameterException('CPU/DRAM error threshold must be positive')

        if config['sensor-reports-frequency'] < 0:
            raise InvalidConfigurationParameterException('Sensor reports frequency must be positive')

        if config['learn-min-samples-required'] < 0 or config['learn-history-window-size'] < 0:
            raise InvalidConfigurationParameterException('Report history parameters must be positive')

        if config['learn-error-window-size'] < 0:
            raise InvalidConfigurationParameterException('Error history window size must be positive')

        if config['learn-error-window-method'] not in ['mean', 'median']:
            raise InvalidConfigurationParameterException('Error window method is not supported')
