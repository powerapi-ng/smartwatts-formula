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

import logging
import signal
import sys
import json
from typing import Dict

from powerapi import __version__ as powerapi_version
from powerapi.dispatcher import RouteTable

from powerapi.cli import ConfigValidator
from powerapi.cli.tools import ComponentSubParser, store_true, ReportModifierGenerator, PullerGenerator, PusherGenerator, CommonCLIParser
from powerapi.message import DispatcherStartMessage
from powerapi.report import HWPCReport, PowerReport
from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.filter import Filter
from powerapi.actor import InitializationException
from powerapi.supervisor import Supervisor

from smartwatts import __version__ as smartwatts_version
from smartwatts.report import FormulaReport
from smartwatts.dispatcher import SmartwattsDispatcherActor
from smartwatts.actor import SmartWattsFormulaActor, SmartwattsValues
from smartwatts.context import SmartWattsFormulaScope, SmartWattsFormulaConfig
from smartwatts.topology import CPUTopology


def generate_smartwatts_parser() -> ComponentSubParser:
    """
    Construct and returns the SmartWatts cli parameters parser.
    :return: SmartWatts cli parameters parser
    """
    parser = CommonCLIParser()

    # Formula control parameters
    parser.add_argument('disable-cpu-formula', help='Disable CPU formula', flag=True, type=bool, default=False, action=store_true)
    parser.add_argument('disable-dram-formula', help='Disable DRAM formula', flag=True, type=bool, default=False, action=store_true)

    # Formula RAPL reference event
    parser.add_argument('cpu-rapl-ref-event', help='RAPL event used as reference for the CPU power models', default='RAPL_ENERGY_PKG')
    parser.add_argument('dram-rapl-ref-event', help='RAPL event used as reference for the DRAM power models', default='RAPL_ENERGY_DRAM')

    # CPU topology information
    parser.add_argument('cpu-tdp', help='CPU TDP (in Watt)', type=int, default=125)
    parser.add_argument('cpu-base-clock', help='CPU base clock (in MHz)', type=int, default=100)
    parser.add_argument('cpu-ratio-min', help='CPU minimal frequency ratio (in MHz)', type=int, default=100)
    parser.add_argument('cpu-ratio-base', help='CPU base frequency ratio (in MHz)', type=int, default=2300)
    parser.add_argument('cpu-ratio-max', help='CPU maximal frequency ratio (In MHz, with Turbo-Boost)', type=int, default=4000)

    # Formula error threshold
    parser.add_argument('cpu-error-threshold', help='Error threshold for the CPU power models (in Watt)', type=float, default=2.0)
    parser.add_argument('dram-error-threshold', help='Error threshold for the DRAM power models (in Watt)', type=float, default=2.0)

    # Sensor information
    parser.add_argument('sensor-report-sampling-interval', help='The frequency with which measurements are made (in milliseconds)', type=int, default=1000)

    # Learning parameters
    parser.add_argument('learn-min-samples-required', help='Minimum amount of samples required before trying to learn a power model', type=int, default=10)
    parser.add_argument('learn-history-window-size', help='Size of the history window used to keep samples to learn from', type=int, default=60)
    parser.add_argument('real-time-mode', help='Pass the wait for reports from 4 ticks to 1', type=bool, default=False)
    return parser


def filter_rule(_):
    """
    Rule of filter. Here none
    """
    return True


def setup_cpu_formula_actor(supervisor, fconf, route_table, report_filter, cpu_topology, formula_pushers, power_pushers):
    """
    Setup CPU formula actor.
    :param supervisor: Actor supervisor
    :param fconf: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param pushers: Reports pushers
    """
    formula_config = SmartWattsFormulaConfig(SmartWattsFormulaScope.CPU, fconf['sensor-report-sampling-interval'],
                                             fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold'],
                                             cpu_topology, fconf['learn-min-samples-required'],
                                             fconf['learn-history-window-size'], fconf['real-time-mode'])
    dispatcher_start_message = DispatcherStartMessage('system', 'cpu_dispatcher', SmartWattsFormulaActor,
                                                      SmartwattsValues(formula_pushers, power_pushers,
                                                                       formula_config), route_table, 'cpu')
    cpu_dispatcher = supervisor.launch(SmartwattsDispatcherActor, dispatcher_start_message)
    report_filter.filter(filter_rule, cpu_dispatcher)


def setup_dram_formula_actor(supervisor, fconf, route_table, report_filter, cpu_topology, formula_pushers, power_pushers):
    """
    Setup DRAM formula actor.
    :param supervisor: Actor supervisor
    :param fconf: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param pushers: Reports pushers
    :return: Initialized DRAM dispatcher actor
    """
    formula_config = SmartWattsFormulaConfig(SmartWattsFormulaScope.DRAM,
                                             fconf['sensor-report-sampling-interval'],
                                             fconf['dram-rapl-ref-event'],
                                             fconf['dram-error-threshold'],
                                             cpu_topology,
                                             fconf['learn-min-samples-required'],
                                             fconf['learn-history-window-size'],
                                             fconf['real-time-mode'])
    dispatcher_start_message = DispatcherStartMessage('system',
                                                      'dram_dispatcher',
                                                      SmartWattsFormulaActor,
                                                      SmartwattsValues(formula_pushers,
                                                                       power_pushers, formula_config),
                                                      route_table, 'dram')
    dram_dispatcher = supervisor.launch(SmartwattsDispatcherActor, dispatcher_start_message)
    report_filter.filter(lambda msg: True, dram_dispatcher)


def run_smartwatts(args) -> None:
    """
    Run PowerAPI with the SmartWatts formula.
    :param args: CLI arguments namespace
    :param logger: Logger to use for the actors
    """
    fconf = args

    logging.info('SmartWatts version %s using PowerAPI version %s', smartwatts_version, powerapi_version)

    if fconf['disable-cpu-formula'] and fconf['disable-dram-formula']:
        logging.error('You need to enable at least one formula')
        return

    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(HWPCDepthLevel.SOCKET, primary=True))

    cpu_topology = CPUTopology(fconf['cpu-tdp'], fconf['cpu-base-clock'], fconf['cpu-ratio-min'], fconf['cpu-ratio-base'], fconf['cpu-ratio-max'])

    report_filter = Filter()

    report_modifier_list = ReportModifierGenerator().generate(fconf)

    supervisor = Supervisor(args['verbose'])

    def term_handler(_, __):
        supervisor.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)
    try:
        logging.info('Starting SmartWatts actors...')

        pusher_generator = PusherGenerator()
        pusher_generator.add_model_factory('FormulaReport', FormulaReport)
        pushers_info = pusher_generator.generate(args)
        pushers_formula = {}
        pushers_power = {}
        for pusher_name in pushers_info:
            pusher_cls, pusher_start_message = pushers_info[pusher_name]
            if pusher_start_message.database.report_type == PowerReport:
                pushers_power[pusher_name] = supervisor.launch(pusher_cls, pusher_start_message)
            elif pusher_start_message.database.report_type == FormulaReport:
                pushers_formula[pusher_name] = supervisor.launch(pusher_cls, pusher_start_message)

        logging.info('CPU formula is %s' % ('DISABLED' if fconf['disable-cpu-formula'] else 'ENABLED'))
        if not fconf['disable-cpu-formula']:
            logging.info('CPU formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold']))
            setup_cpu_formula_actor(supervisor, fconf, route_table, report_filter, cpu_topology, pushers_formula, pushers_power)

            logging.info('DRAM formula is %s' % ('DISABLED' if fconf['disable-dram-formula'] else 'ENABLED'))
        if not fconf['disable-dram-formula']:
            logging.info('DRAM formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['dram-rapl-ref-event'], fconf['dram-error-threshold']))
            setup_dram_formula_actor(supervisor, fconf, route_table, report_filter, cpu_topology, pushers_formula, pushers_power)

        pullers_info = PullerGenerator(report_filter, report_modifier_list).generate(args)
        for puller_name in pullers_info:
            puller_cls, puller_start_message = pullers_info[puller_name]
            supervisor.launch(puller_cls, puller_start_message)
    except InitializationException as exn:
        logging.error('Actor initialization error: ' + exn.msg)
        supervisor.shutdown()
        sys.exit(-1)

    logging.info('SmartWatts is now running...')
    supervisor.monitor()
    logging.info('SmartWatts is shutting down...')


def get_config_file(argv):
    """
    Get config file from argv
    """
    i = 0
    for s in argv:
        if s == '--config-file':
            if i + 1 == len(argv):
                logging.error("config file path needed with argument --config-file")
                sys.exit(-1)
            return argv[i + 1]
        i += 1
    return None


def get_config_from_file(file_path):
    """
    Get the config from the config file
    """
    config_file = open(file_path, 'r')
    return json.load(config_file)


class SmartwattsConfigValidator(ConfigValidator):
    """
    Class used that check the config extracted and verify it conforms to constraints
    """
    @staticmethod
    def validate(config: Dict):
        if not ConfigValidator.validate(config):
            return False

        if 'disable-cpu-formula' not in config:
            config['disable-cpu-formula'] = False
        if 'disable-dram-formula' not in config:
            config['disable-dram-formula'] = False
        if 'cpu-rapl-ref-event' not in config:
            config['cpu-rapl-ref-event'] = 'RAPL_ENERGY_PKG'
        if 'dram-rapl-ref-event' not in config:
            config['dram-rapl-ref-event'] = 'RAPL_ENERGY_DRAM'
        if 'cpu-tdp' not in config:
            config['cpu-tdp'] = 125
        if 'cpu-base-clock' not in config:
            config['cpu-base-clock'] = 100
        if 'sensor-report-sampling-interval' not in config:
            config['sensor-report-sampling-interval'] = 1000
        if 'learn-min-samples-required' not in config:
            config['learn-min-samples-required'] = 10
        if 'learn-history-window-size' not in config:
            config['learn-history-window-size'] = 60
        if 'real-time-mode' not in config:
            config['real-time-mode'] = False

        # Model use frequency in 100MHz
        if 'cpu-ratio-base' in config:
            config['cpu-ratio-base'] = config['cpu-ratio-base'] / 100
        if 'cpu-ratio-min' in config:
            config['cpu-ratio-min'] = config['cpu-ratio-min'] / 100
        if 'cpu-ratio-max' in config:
            config['cpu-ratio-max'] = config['cpu-ratio-max'] / 100

        return True


def get_config_from_cli():
    """
    Get he config from the cli args
    """
    parser = generate_smartwatts_parser()
    return parser.parse_argv()


if __name__ == "__main__":
    config_file_path = get_config_file(sys.argv)
    conf = get_config_from_file(config_file_path) if config_file_path is not None else get_config_from_cli()
    if not SmartwattsConfigValidator.validate(conf):
        sys.exit(-1)
    logging.basicConfig(level=logging.WARNING if conf['verbose'] else logging.INFO)
    logging.captureWarnings(True)

    logging.debug(str(conf))
    run_smartwatts(conf)
    sys.exit(0)
