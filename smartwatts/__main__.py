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

from powerapi import __version__ as powerapi_version
from powerapi.actor import ActorInitError
from powerapi.backendsupervisor import BackendSupervisor
from powerapi.cli.parser import ComponentSubParser
from powerapi.cli.tools import CommonCLIParser, PusherGenerator, PullerGenerator
from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.dispatcher import DispatcherActor, RouteTable
from powerapi.filter import Filter
from powerapi.report import HWPCReport

from smartwatts import __version__ as smartwatts_version
from smartwatts.actor import SmartWattsFormulaActor, SmartWattsFormulaConfig
from smartwatts.context import SmartWattsFormulaScope
from smartwatts.topology import CPUTopology


def generate_smartwatts_parser() -> ComponentSubParser:
    """
    Construct and returns the SmartWatts cli parameters parser.
    :return: SmartWatts cli parameters parser
    """
    parser = ComponentSubParser('smartwatts')

    # Formula control parameters
    parser.add_argument('disable-cpu-formula', help='', type=bool, default=False)
    parser.add_argument('disable-dram-formula', help='', type=bool, default=False)

    # Formula RAPL reference event
    parser.add_argument('cpu-rapl-ref-event', help='RAPL event used as reference for the CPU power models', default='RAPL_ENERGY_PKG')
    parser.add_argument('dram-rapl-ref-event', help='RAPL event used as reference for the DRAM power models', default='RAPL_ENERGY_DRAM')

    # CPU topology information
    parser.add_argument('cpu-tdp', help='CPU TDP (in Watt)', type=int, default=0)
    parser.add_argument('cpu-base-clock', help='CPU base clock (in MHz)', type=int, default=100)
    parser.add_argument('cpu-ratio-min', help='CPU minimal frequency ratio', type=int, default=10)
    parser.add_argument('cpu-ratio-base', help='CPU base frequency ratio', type=int, default=23)
    parser.add_argument('cpu-ratio-max', help='CPU maximal frequency ratio (with Turbo-Boost)', type=int, default=40)

    # Formula error threshold
    parser.add_argument('cpu-error-threshold', help='Error threshold for the CPU power models (in Watt)', type=float, default=2.0)
    parser.add_argument('dram-error-threshold', help='Error threshold for the DRAM power models (in Watt)', type=float, default=2.0)

    # Sensor information
    parser.add_argument('reports-frequency', help='The frequency with which measurements are made (in milliseconds)', default=1000)

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
        config = SmartWattsFormulaConfig(SmartWattsFormulaScope.CPU, fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold'], cpu_topology)
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
        config = SmartWattsFormulaConfig(scope, fconf['dram-rapl-ref-event'], fconf['dram-error-threshold'], cpu_topology)
        return SmartWattsFormulaActor(name, pushers, config)

    dram_dispatcher = DispatcherActor('dram_dispatcher', dram_formula_factory, route_table)
    report_filter.filter(lambda msg: True, dram_dispatcher)
    return dram_dispatcher


def run_smartwatts(args, logger) -> None:
    """
    Run PowerAPI with the SmartWatts formula.
    :param args: CLI arguments namespace
    :param logger: Logger to use for the actors
    """
    fconf = args['formula']['smartwatts']
    actors = []

    logger.info('SmartWatts version %s using PowerAPI version %s', smartwatts_version, powerapi_version)

    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(HWPCDepthLevel.SOCKET, primary=True))

    cpu_topology = CPUTopology(fconf['cpu-tdp'], fconf['cpu-base-clock'], fconf['cpu-ratio-min'], fconf['cpu-ratio-base'], fconf['cpu-ratio-max'])
    report_filter = Filter()

    pushers = PusherGenerator().generate(args)
    actors += pushers

    logger.info('CPU formula is %s' % ('DISABLED' if fconf['disable-cpu-formula'] else 'ENABLED'))
    if not fconf['disable-cpu-formula']:
        logger.info('CPU formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold']))
        actors += setup_cpu_formula_actor(fconf, route_table, report_filter, cpu_topology, pushers)

    logger.info('DRAM formula is %s' % ('DISABLED' if fconf['disable-dram-formula'] else 'ENABLED'))
    if not fconf['disable-dram-formula']:
        logger.info('DRAM formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['dram-rapl-ref-event'], fconf['dram-error-threshold']))
        actors += setup_dram_formula_actor(fconf, route_table, report_filter, cpu_topology, pushers)

    pullers = PullerGenerator(report_filter).generate(args)
    actors += pullers

    def term_handler(_, __):
        for actor in actors:
            actor.soft_kill()
        exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    supervisor = BackendSupervisor(config['stream'])
    try:
        logger.info('Starting SmartWatts actors...')
        for actor in actors:
            supervisor.launch_actor(actor)
    except ActorInitError as exn:
        logger.error('Actor initialization error: ' + exn.message)
        supervisor.kill_actors()

    logger.info('Actors initialized, SmartWatts is now running...')
    supervisor.join()


if __name__ == "__main__":
    parser = CommonCLIParser()
    parser.add_formula_subparser('formula', generate_smartwatts_parser(), 'specify the formula to use')
    config = parser.parse_argv()

    logger = logging.getLogger('main_logger')
    logger.setLevel(config['verbose'])
    logger.addHandler(logging.StreamHandler())

    # FIXME: Better error handling when the user doesn't provide a formula parameter.
    try:
        config['formula']['smartwatts']
    except KeyError:
        exit(-1)

    run_smartwatts(config, logger)
    exit(0)
