# CloudJoule — for powerAPI
#
# Copyright (c) 2022 Orange - All right reserved
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import logging
import os

from powerapi.cli import ConfigValidator

"""
This module supports configuring some key parameter using environment variables.
This is useful, and recommended (cf. twelve-factor app), when running in a environment where changing 
the configuration file across deployments (e.g. k8s in our case).

At the moment, only a subset of configuration parameters are supported.
It's currently quite a hack and should probably be merged with the existing 
configuration mechanism, which currently supports file and cli arguments.
"""

logger = logging.getLogger("node-power-exporter.configuration")

# connection mode for K8S API, manual, local or cluster
K8SAPI_MODE="cluster"

LOG_LEVEL = "INFO"

# The frequency with which measurements are made (in milliseconds)
REPORT_FREQ = 1000

# Error threshold for the power models (in Watt) - can be set for CPU and DRAM:
ERROR_THRESHOLD = 2

# Minimum amount of samples required before trying to learn a power model:
MIN_SAMPLES_REQUIRED = 10

# Size of the history window used to keep samples to learn from:
HISTORY_WINDOW_SIZE = 60

# Frequencies configuration
MIN_FREQ = None
MAX_FREQ = None
BASE_FREQ = None

# Number of sockets
SOCKET_COUNT = None

# TDP
CPU_TDP = 125

BASE_CLOCK = 100

EXPORTER_LABELS=["app","service","env"]

EXPORTER_PORT=8124

def load_config_from_env():
    global LOG_LEVEL, REPORT_FREQ, ERROR_THRESHOLD,\
        MIN_SAMPLES_REQUIRED, HISTORY_WINDOW_SIZE, \
        MIN_FREQ, MAX_FREQ, BASE_FREQ, SOCKET_COUNT, CPU_TDP, \
        K8SAPI_MODE, EXPORTER_LABELS, EXPORTER_PORT

    # Get the configuration from environment variables:
    try:
        K8SAPI_MODE = safe_get_env("K8SAPI_MODE", str)
        LOG_LEVEL = safe_get_env("LOG_LEVEL", str)
        REPORT_FREQ = safe_get_env("REPORT_FREQ", int)
        ERROR_THRESHOLD = safe_get_env("ERROR_THRESHOLD", float)
        MIN_SAMPLES_REQUIRED = safe_get_env("MIN_SAMPLES_REQUIRED", int)
        HISTORY_WINDOW_SIZE = safe_get_env("HISTORY_WINDOW_SIZE", int)
        CPU_TDP = safe_get_env("CPU_TDP", int)
        EXPORTER_PORT = safe_get_env("EXPORTER_PORT", int)
        EXPORTER_LABELS = safe_get_env("EXPORTER_LABELS", to_list)
        EXPORTER_LABELS = [f"label_{label}" for label in EXPORTER_LABELS]

        # Frequencies configuration
        MIN_FREQ = int(float(os.environ["MIN_FREQ"]) / 100)
        MAX_FREQ = int(float(os.environ["MAX_FREQ"]) / 100)
        BASE_FREQ = int(float(os.environ["BASE_FREQ"]) / 100)

        # Number of sockets
        SOCKET_COUNT = int(os.environ["SOCKET_COUNT"])

    except Exception as e:
        logger.error(f"Invalid configuration for ENV : {e}")
        raise


def to_list(s):
    return [p.strip() for p in  s.split(",")]


def safe_get_env(ENV_NAME, conversion):
    try:
        return conversion(os.environ[ENV_NAME])
    except KeyError:
        pass
        return globals()[ENV_NAME]


def get_smartwatt_config_map():
    """
    Returns the configuration as a map with the same keys
    than used and expected by smartwatt.
    """
    if SOCKET_COUNT is None:
        raise RuntimeError("Load config must have been called before !")
    conf = {
        # Constant conf item in our case
        "stream": True,
        "actor_system": "simpleSystemBase",
        "disable-cpu-formula": False,
        "disable-dram-formula": True,
        "cpu-rapl-ref-event": "RAPL_ENERGY_PKG",
        "dram-rapl-ref-event": "RAPL_ENERGY_DRAM",
        "verbose": LOG_LEVEL == "DEBUG",  
        # TODO: not sure what that means
        "real-time-mode": False,
        # Items from env variables
        "cpu-tdp": CPU_TDP,
        "cpu-base-clock": BASE_CLOCK,
        "sensor-report-sampling-interval": REPORT_FREQ,
        "learn-min-samples-required": MIN_SAMPLES_REQUIRED,
        "learn-history-window-size": HISTORY_WINDOW_SIZE,
        "cpu-error-threshold": ERROR_THRESHOLD,
        # Model use frequency in 100MHz
        "cpu-frequency-base": BASE_FREQ,
        "cpu-frequency-min": MIN_FREQ,
        "cpu-frequency-max": MAX_FREQ,
        "k8sapi_mode": K8SAPI_MODE
    }

    # Output hardcoded to our custom prometheus exporter
    # TODO : move this to the external configuration file ?
    conf["output"] = {
        "pusher_power": {
            "type": "cloudjoule_prom",
            "uri": "127.0.0.1",
            "port": EXPORTER_PORT,
            "metric_name": "cloudjoule",
            "metric_description": "cloudjoule energy metric",
            "model": "PowerReport",
            "labels" : EXPORTER_LABELS
        }
    }

    # Input hardcoded to a locally running sensor outputting
    # to a socket port 12000
    conf["input"] = {
        "socket_puller": {
            "model": "HWPCReport",
            "type": "socket",
            "uri": "127.0.0.1",
            "port": 12000,
        }
    }

    # make sure the conf is valid for power api
    ConfigValidator.validate(conf)
    return conf
