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

    # Formula RAPL reference event
    parser.add_argument('cpu-rapl-ref-event', help='RAPL event used as reference for the CPU power models', default='RAPL_ENERGY_PKG')
    parser.add_argument('dram-rapl-ref-event', help='RAPL event used as reference for the DRAM power models', default='RAPL_ENERGY_DRAM')

    # CPU topology information
    parser.add_argument('cpu-base-clock', help='CPU base clock (in MHz)', type=int, default=100)
    parser.add_argument('cpu-ratio-min', help='CPU minimal frequency ratio', type=int, default=10)
    parser.add_argument('cpu-ratio-base', help='CPU base frequency ratio', type=int, default=23)
    parser.add_argument('cpu-ratio-max', help='CPU maximal frequency ratio (with Turbo-Boost)', type=int, default=40)

    # Formula error threshold
    parser.add_argument('cpu-error-threshold', help='Error threshold for the CPU power models (in Watt)', type=float, default=2.0)
    parser.add_argument('dram-error-threshold', help='Error threshold for the DRAM power models (in Watt)', type=float, default=2.0)

    return parser


def run_smartwatts(args, logger):
    """
    Run PowerAPI with the SmartWatts formula.
    :param args: CLI arguments namespace
    :param logger: Log level to use for the actors
    """

    fconf = args['formula']['smartwatts']

    # Print configuration
    logger.info('SmartWatts version %s using PowerAPI version %s', smartwatts_version, powerapi_version)
    logger.info('CPU formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold']))
    logger.info('DRAM formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (fconf['dram-rapl-ref-event'], fconf['dram-error-threshold']))

    # Sensor reports route table
    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(HWPCDepthLevel.SOCKET, primary=True))

    # Shared parameters
    pushers = PusherGenerator().generate(config)
    cpu_topology = CPUTopology(fconf['cpu-base-clock'], fconf['cpu-ratio-min'], fconf['cpu-ratio-base'], fconf['cpu-ratio-max'])

    # CPU formula dispatcher
    def cpu_formula_factory(name: str, _):
        scope = SmartWattsFormulaScope.CPU
        config = SmartWattsFormulaConfig(scope, fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold'], cpu_topology)
        return SmartWattsFormulaActor(name, pushers, config)

    cpu_dispatcher = DispatcherActor('cpu_dispatcher', cpu_formula_factory, route_table)

    # DRAM formula dispatcher
    def dram_formula_factory(name: str, _):
        scope = SmartWattsFormulaScope.DRAM
        config = SmartWattsFormulaConfig(scope, fconf['cpu-rapl-ref-event'], fconf['cpu-error-threshold'], cpu_topology)
        return SmartWattsFormulaActor(name, pushers, config)

    dram_dispatcher = DispatcherActor('dram_dispatcher', dram_formula_factory, route_table)

    # reports pullers
    report_filter = Filter()
    report_filter.filter(lambda msg: True, cpu_dispatcher)
    report_filter.filter(lambda msg: True, dram_dispatcher)
    pullers = PullerGenerator(report_filter).generate(config)

    def term_handler(_, __):
        for puller in pullers.values():
            puller.soft_kill()

        cpu_dispatcher.soft_kill()
        dram_dispatcher.soft_kill()

        for pusher in pushers.values():
            pusher.soft_kill()

        exit(0)

    # TERM/INT signals handler
    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    logger.info('Starting SmartWatts actors...')

    # Actors supervision
    supervisor = BackendSupervisor(config['stream'])
    try:
        for pusher in pushers.values():
            supervisor.launch_actor(pusher)

        supervisor.launch_actor(cpu_dispatcher)
        supervisor.launch_actor(dram_dispatcher)

        for puller in pullers.values():
            supervisor.launch_actor(puller)
    except ActorInitError as exn:
        logger.error('Actor initialisation error: ' + exn.message)
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

    run_smartwatts(config, logger)
