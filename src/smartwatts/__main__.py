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

import logging
import signal
import sys
from collections import OrderedDict
from typing import Dict

from powerapi import __version__ as powerapi_version
from powerapi.backend_supervisor import BackendSupervisor
from powerapi.cli.binding_manager import PreProcessorBindingManager
from powerapi.cli.common_cli_parsing_manager import CommonCLIParsingManager
from powerapi.cli.config_parser import store_true
from powerapi.cli.generator import PusherGenerator, PullerGenerator, PreProcessorGenerator
from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.dispatcher import DispatcherActor, RouteTable
from powerapi.exception import PowerAPIException, MissingArgumentException, NotAllowedArgumentValueException, FileDoesNotExistException
from powerapi.filter import Filter
from powerapi.report import HWPCReport

from smartwatts import __version__ as smartwatts_version
from smartwatts.actor import SmartWattsFormulaScope, SmartWattsFormulaConfig, SmartWattsFormulaActorFactory
from smartwatts.cli import SmartWattsConfigValidator
from smartwatts.exceptions import InvalidConfigurationParameterException
from smartwatts.model import CPUTopology


def generate_smartwatts_parser() -> CommonCLIParsingManager:
    """
    Construct and returns the SmartWatts cli parameters parser.
    :return: SmartWatts cli parameters parser
    """
    pm = CommonCLIParsingManager()

    # Formula control parameters
    pm.add_argument('disable-cpu-formula', help_text='Disable CPU formula', is_flag=True, argument_type=bool, default_value=False, action=store_true)
    pm.add_argument('disable-dram-formula', help_text='Disable DRAM formula', is_flag=True, argument_type=bool, default_value=False, action=store_true)

    # Formula RAPL reference event
    pm.add_argument('cpu-rapl-ref-event', help_text='RAPL event used as reference for the CPU power models', default_value='RAPL_ENERGY_PKG')
    pm.add_argument('dram-rapl-ref-event', help_text='RAPL event used as reference for the DRAM power models', default_value='RAPL_ENERGY_DRAM')

    # CPU topology information
    pm.add_argument('cpu-tdp', help_text='CPU TDP (in Watt)', argument_type=int, default_value=400)
    pm.add_argument('cpu-base-clock', help_text='CPU base clock (in MHz)', argument_type=int, default_value=100)
    pm.add_argument('cpu-base-freq', help_text='CPU base frequency (in MHz)', argument_type=int, default_value=2100)

    # Formula error threshold
    pm.add_argument('cpu-error-threshold', help_text='Error threshold for the CPU power models (in Watt)', argument_type=float, default_value=2.0)
    pm.add_argument('dram-error-threshold', help_text='Error threshold for the DRAM power models (in Watt)', argument_type=float, default_value=2.0)

    # Sensor information
    pm.add_argument('sensor-reports-frequency', help_text='The frequency with which measurements are made (in milliseconds)', argument_type=int, default_value=1000)

    # Learning parameters
    pm.add_argument('learn-min-samples-required', help_text='Minimum amount of samples required before trying to learn a power model', argument_type=int, default_value=10)
    pm.add_argument('learn-history-window-size', help_text='Size of the history window used to keep samples to learn from', argument_type=int, default_value=60)
    pm.add_argument('learn-error-window-size', help_text='Size of the error window used to trigger the learning of a new power model', argument_type=int, default_value=60)
    pm.add_argument('learn-error-window-method', help_text='Method used to compute the error window (supported: median, mean)', default_value='median')

    return pm


def generate_formula_configuration(config: Dict, cpu_topology: CPUTopology, scope: SmartWattsFormulaScope) -> SmartWattsFormulaConfig:
    """
    Generate a SmartWatts actor configuration.
    """
    reports_freq = config['sensor-reports-frequency']
    rapl_event = config[f'{scope.value}-rapl-ref-event']
    error_threshold = config[f'{scope.value}-error-threshold']
    min_samples = config['learn-min-samples-required']
    history_window_size = config['learn-history-window-size']
    real_time_mode = config['stream']
    error_window_size = config['learn-error-window-size']
    error_window_method = config['learn-error-window-method']
    return SmartWattsFormulaConfig(scope, reports_freq, rapl_event, error_threshold, cpu_topology, min_samples, history_window_size, real_time_mode, error_window_size, error_window_method)


def setup_cpu_formula_dispatcher(config, route_table, report_filter, cpu_topology, pushers) -> DispatcherActor:
    """
    Setup CPU formula actor.
    :param config: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param pushers: Reports pushers
    :return: Initialized CPU dispatcher actor
    """
    formula_config = generate_formula_configuration(config, cpu_topology, SmartWattsFormulaScope.CPU)
    formula_factory = SmartWattsFormulaActorFactory(formula_config)
    cpu_dispatcher = DispatcherActor('cpu_dispatcher', formula_factory, pushers, route_table)
    report_filter.filter(lambda msg: True, cpu_dispatcher)
    return cpu_dispatcher


def setup_dram_formula_dispatcher(config, route_table, report_filter, cpu_topology, pushers) -> DispatcherActor:
    """
    Setup DRAM formula actor.
    :param config: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param pushers: Reports pushers
    :return: Initialized DRAM dispatcher actor
    """
    formula_config = generate_formula_configuration(config, cpu_topology, SmartWattsFormulaScope.DRAM)
    formula_factory = SmartWattsFormulaActorFactory(formula_config)
    dram_dispatcher = DispatcherActor('dram_dispatcher', formula_factory, pushers, route_table)
    report_filter.filter(lambda msg: True, dram_dispatcher)
    return dram_dispatcher


def run_smartwatts(config) -> None:
    """
    Run PowerAPI with the SmartWatts formula.
    :param config: CLI arguments namespace
    """
    logging.info('SmartWatts version %s based on PowerAPI version %s', smartwatts_version, powerapi_version)

    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(HWPCDepthLevel.SOCKET, primary=True))

    cpu_topology = CPUTopology(config['cpu-tdp'], config['cpu-base-clock'], 1, int(config['cpu-base-freq'] / config['cpu-base-clock']), 100)

    report_filter = Filter()
    pullers = PullerGenerator(report_filter).generate(config)

    pushers = PusherGenerator().generate(config)

    dispatchers = {}

    logging.info('CPU formula is %s', 'DISABLED' if config['disable-cpu-formula'] else 'ENABLED')
    if not config['disable-cpu-formula']:
        logging.info('CPU formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW', config['cpu-rapl-ref-event'], config['cpu-error-threshold'])
        dispatchers['cpu'] = setup_cpu_formula_dispatcher(config, route_table, report_filter, cpu_topology, pushers)

    logging.info('DRAM formula is %s', 'DISABLED' if config['disable-dram-formula'] else 'ENABLED')
    if not config['disable-dram-formula']:
        logging.info('DRAM formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW', config['dram-rapl-ref-event'], config['dram-error-threshold'])
        dispatchers['dram'] = setup_dram_formula_dispatcher(config, route_table, report_filter, cpu_topology, pushers)

    if 'pre-processor' in config:
        pre_processors = PreProcessorGenerator().generate(config)

        binding_manager = PreProcessorBindingManager(pullers, pre_processors)
        binding_manager.process_bindings()
    else:
        pre_processors = {}

    actors = OrderedDict(**pushers, **dispatchers, **pre_processors, **pullers)
    supervisor = BackendSupervisor(config['stream'])

    def term_handler(_, __):
        supervisor.kill_actors()
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    for _, actor in actors.items():
        try:
            logging.debug('Initializing actor %s...', actor.name)
            supervisor.launch_actor(actor)
        except PowerAPIException:
            logging.error('Failed to initialize actor %s', actor.name)
            supervisor.kill_actors()
            sys.exit(1)

    logging.info('SmartWatts is now running...')
    supervisor.join()
    logging.info('SmartWatts is shutting down...')


if __name__ == "__main__":
    args_parser = generate_smartwatts_parser()
    args = args_parser.parse()

    try:
        SmartWattsConfigValidator().validate(args)
    except InvalidConfigurationParameterException as exn:
        logging.error('Invalid configuration: %s', exn)
        sys.exit(1)
    except MissingArgumentException as exn:
        logging.error('Missing argument: %s', exn)
        sys.exit(1)
    except NotAllowedArgumentValueException as exn:
        logging.error('Not Allowed Argument: %s', exn)
        sys.exit(1)
    except FileDoesNotExistException as exn:
        logging.error('File does not exist: %s', exn)
        sys.exit(1)

    LOGGING_LEVEL = logging.DEBUG if args['verbose'] else logging.INFO
    LOGGING_FORMAT = '%(asctime)s - %(process)d - %(processName)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)

    run_smartwatts(args)
    sys.exit(0)
