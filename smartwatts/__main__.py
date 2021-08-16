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
from collections import OrderedDict
from typing import Dict

from powerapi import __version__ as powerapi_version
from powerapi.actor import ActorInitError
from powerapi.backendsupervisor import BackendSupervisor
from powerapi.cli.parser import ComponentSubParser, store_true
from powerapi.cli.tools import CommonCLIParser, PusherGenerator, PullerGenerator, ReportModifierGenerator
from powerapi.cli import ConfigValidator
from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.dispatcher import DispatcherActor, RouteTable
from powerapi.filter import Filter
from powerapi.report import HWPCReport

from smartwatts import __version__ as smartwatts_version
from smartwatts.actor import SmartWattsFormulaActor
from smartwatts.context import SmartWattsFormulaScope, SmartWattsFormulaConfig
from smartwatts.topology import CPUTopology


def generate_smartwatts_parser() -> ComponentSubParser:
    """
    Construct and returns the SmartWatts cli parameters parser.
    :return: SmartWatts cli parameters parser
    """
    parser = ComponentSubParser('smartwatts')

    # Formula control parameters
    parser.add_argument('disable-cpu-formula', help='Disable CPU formula', flag=True, type=bool, default=False, action=store_true)
    parser.add_argument('disable-dram-formula', help='Disable DRAM formula', flag=True, type=bool, default=False, action=store_true)

    # Formula RAPL reference event
    parser.add_argument('cpu-rapl-ref-event', help='RAPL event used as reference for the CPU power models', default='RAPL_ENERGY_PKG')
    parser.add_argument('dram-rapl-ref-event', help='RAPL event used as reference for the DRAM power models', default='RAPL_ENERGY_DRAM')

    # CPU topology information
    parser.add_argument('cpu-tdp', help='CPU TDP (in Watt)', type=int, default=125)
    parser.add_argument('cpu-base-clock', help='CPU base clock (in MHz)', type=int, default=100)
    parser.add_argument('cpu-ratio-min', help='CPU minimal frequency ratio', type=int, default=10)
    parser.add_argument('cpu-ratio-base', help='CPU base frequency ratio', type=int, default=23)
    parser.add_argument('cpu-ratio-max', help='CPU maximal frequency ratio (with Turbo-Boost)', type=int, default=40)

    # Formula error threshold
    parser.add_argument('cpu-error-threshold', help='Error threshold for the CPU power models (in Watt)', type=float, default=2.0)
    parser.add_argument('dram-error-threshold', help='Error threshold for the DRAM power models (in Watt)', type=float, default=2.0)

    # Sensor information
    parser.add_argument('sensor-reports-frequency', help='The frequency with which measurements are made (in milliseconds)', type=int, default=1000)

    # Learning parameters
    parser.add_argument('learn-min-samples-required', help='Minimum amount of samples required before trying to learn a power model', type=int, default=10)
    parser.add_argument('learn-history-window-size', help='Size of the history window used to keep samples to learn from', type=int, default=60)

    return parser


def setup_cpu_formula_actor(fconf, route_table, report_filter, cpu_topology, pushers) -> DispatcherActor:
    """
    Setup CPU formula actor.
    :param fconf: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param pushers: Reports pushers
    :return: Initialized CPU dispatcher actor
    """
    def cpu_formula_factory(name: str, _):
        scope = SmartWattsFormulaScope.CPU
        config = SmartWattsFormulaConfig(scope, fconf['sensor-reports-frequency'], fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold'], cpu_topology, fconf['learn-min-samples-required'], fconf['learn-history-window-size'])
        return SmartWattsFormulaActor(name, pushers, config)

    cpu_dispatcher = DispatcherActor('cpu_dispatcher', cpu_formula_factory, route_table)
    report_filter.filter(lambda msg: True, cpu_dispatcher)
    return cpu_dispatcher


def setup_dram_formula_actor(fconf, route_table, report_filter, cpu_topology, pushers) -> DispatcherActor:
    """
    Setup DRAM formula actor.
    :param fconf: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param pushers: Reports pushers
    :return: Initialized DRAM dispatcher actor
    """
    def dram_formula_factory(name: str, _):
        scope = SmartWattsFormulaScope.DRAM
        config = SmartWattsFormulaConfig(scope, fconf['sensor-reports-frequency'], fconf['dram-rapl-ref-event'], fconf['dram-error-threshold'], cpu_topology, fconf['learn-min-samples-required'], fconf['learn-min-samples-required'])
        return SmartWattsFormulaActor(name, pushers, config)

    dram_dispatcher = DispatcherActor('dram_dispatcher', dram_formula_factory, route_table)
    report_filter.filter(lambda msg: True, dram_dispatcher)
    return dram_dispatcher


def run_smartwatts(args) -> None:
    """
    Run PowerAPI with the SmartWatts formula.
    :param args: CLI arguments namespace
    :param logger: Logger to use for the actors
    """
    fconf = args['formula']

    logging.info('SmartWatts version %s using PowerAPI version %s', smartwatts_version, powerapi_version)

    if fconf['disable-cpu-formula'] and fconf['disable-dram-formula']:
        logging.error('You need to enable at least one formula')
        return

    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(HWPCDepthLevel.SOCKET, primary=True))

    cpu_topology = CPUTopology(fconf['cpu-tdp'], fconf['cpu-base-clock'], fconf['cpu-ratio-min'], fconf['cpu-ratio-base'], fconf['cpu-ratio-max'])

    report_filter = Filter()

    report_modifier_list = ReportModifierGenerator().generate(config)
    
    pullers = PullerGenerator(report_filter, report_modifier_list).generate(args)

    pushers = PusherGenerator().generate(args)

    dispatchers = {}

    logging.info('CPU formula is %s' % ('DISABLED' if fconf['disable-cpu-formula'] else 'ENABLED'))
    if not fconf['disable-cpu-formula']:
        logging.info('CPU formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold']))
        dispatchers['cpu'] = setup_cpu_formula_actor(fconf, route_table, report_filter, cpu_topology, pushers)

    logging.info('DRAM formula is %s' % ('DISABLED' if fconf['disable-dram-formula'] else 'ENABLED'))
    if not fconf['disable-dram-formula']:
        logging.info('DRAM formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['dram-rapl-ref-event'], fconf['dram-error-threshold']))
        dispatchers['dram'] = setup_dram_formula_actor(fconf, route_table, report_filter, cpu_topology, pushers)

    actors = OrderedDict(**pushers, **dispatchers, **pullers)

    def term_handler(_, __):
        for _, actor in actors.items():
            actor.soft_kill()
        exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    supervisor = BackendSupervisor(args['stream'])
    try:
        logging.info('Starting SmartWatts actors...')
        for actor_list in [pushers, dispatchers, pullers]:
            for _, actor in actor_list.items():
                supervisor.launch_actor(actor)
    except ActorInitError as exn:
        logging.error('Actor initialization error: ' + exn.message)
        supervisor.kill_actors()

    logging.info('SmartWatts is now running...')
    supervisor.join()
    logging.info('SmartWatts is shutting down...')


def get_config_file(argv):
    i = 0
    for s in argv:
        if s == '--config-file':
            if i + 1 == len(argv):
                logging.error("config file path needed with argument --config-file")
                exit(-1)
            return argv[i+1]
        i += 1
    return None


def get_config_from_file(file_path):
    config_file = open(file_path, 'r')
    return json.load(config_file)


class SmartwattsConfigValidator(ConfigValidator):
    @staticmethod
    def validate(config: Dict):
        if not ConfigValidator.validate(config):
            return False
        if 'formula' not in config:
            logging.error('No configuration found for smartwatts formula')
            return False

        if 'disable-cpu-formula' not in config['formula']:
            config['formula']['disable-cpu-formula'] = False
        if 'disable-dram-formula' not in config['formula']:
            config['formula']['disable-dram-formula'] = False
        if 'cpu-rapl-ref-event' not in config['formula']:
            config['formula']['cpu-rapl-ref-event'] = 'RAPL_ENERGY_PKG'
        if 'dram-rapl-ref-event' not in config['formula']:
            config['formula']['dram-rapl-ref-event'] = 'RAPL_ENERGY_DRAM'
        if 'cpu-tdp' not in config['formula']:
            config['formula']['cpu-tdp'] = 125
        if 'cpu-base-clock' not in config['formula']:
            config['formula']['cpu-base-clock'] = 100
        if 'sensor-reports-frequency' not in config['formula']:
            config['formula']['sensor-reports-frequency'] = 1000
        if 'learn-min-samples-required' not in config['formula']:
            config['formula']['learn-min-samples-required'] = 10
        if 'learn-history-window-size' not in config['formula']:
            config['formula']['learn-history-window-size'] = 60
        return True
        

def get_config_from_cli():
    parser = CommonCLIParser()
    parser.add_component_subparser('formula', generate_smartwatts_parser(), 'specify the formula to use')
    return parser.parse_argv()


if __name__ == "__main__":
    config_file_path = get_config_file(sys.argv)
    config = get_config_from_file(config_file_path) if config_file_path is not None else get_config_from_cli()
    if not SmartwattsConfigValidator.validate(config):
        exit(-1)
    print(config)

    logging.basicConfig(level=logging.WARNING if config['verbose'] else logging.INFO)
    logging.captureWarnings(True)

    run_smartwatts(config)
    exit(0)
