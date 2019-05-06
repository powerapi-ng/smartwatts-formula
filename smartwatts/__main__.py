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

import argparse
import logging
import signal
import zmq

from powerapi import __version__ as powerapi_version
from powerapi.actor import ActorInitError, Supervisor
from powerapi.database import MongoDB
from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.dispatcher import DispatcherActor, RouteTable
from powerapi.filter import Filter
from powerapi.puller import PullerActor
from powerapi.pusher import PusherActor
from powerapi.report import HWPCReport, PowerReport
from powerapi.report.formula_report import FormulaReport
from powerapi.report_model import HWPCModel

from smartwatts import __version__ as smartwatts_version
from smartwatts.actor import FormulaScope, SmartWattsFormulaActor
from smartwatts.topology import CPUTopology


class BadActorInitializationError(Exception):
    """
    Error if actor doesn't answer with "OKMessage"
    """


def parse_cli_args():
    """
    Parse the CLI arguments.
    :return: Namespace with parsed CLI arguments
    """
    parser = argparse.ArgumentParser(description='SmartWatts power meter version %s' % smartwatts_version)

    # MongoDB options
    parser.add_argument('--mongodb-uri', help='MongoDB server URI', required=True)
    parser.add_argument('--mongodb-database', help='MongoDB database name', required=True)
    parser.add_argument('--mongodb-sensor-collection', help='MongoDB collection where the sensor reports are stored', default='sensor')
    parser.add_argument('--mongodb-powermeter-collection', help='MongoDB collection where the power estimations will be stored', default='powermeter')
    parser.add_argument('--mongodb-formula-collection', help='MongoDB collection where information about the used formula will be stored', default='formula')

    # Formula modes
    parser.add_argument('--system-only', help='Only compute the power estimations for the System target', default=False)

    # Formula RAPL reference event
    parser.add_argument('--cpu-rapl-ref-event', help='RAPL event used as reference for the CPU power models', default='RAPL_ENERGY_PKG')
    parser.add_argument('--dram-rapl-ref-event', help='RAPL event used as reference for the DRAM power models', default='RAPL_ENERGY_DRAM')

    # CPU topology information
    parser.add_argument('--cpu-base-clock', help='CPU base clock (in MHz)', type=int, default=100)
    parser.add_argument('--cpu-ratio-min', help='CPU minimal frequency ratio', type=int, default=10)
    parser.add_argument('--cpu-ratio-base', help='CPU base frequency ratio', type=int, default=23)
    parser.add_argument('--cpu-ratio-max', help='CPU maximal frequency ratio (with Turbo-Boost)', type=int, default=40)

    # Formula error threshold
    parser.add_argument('--cpu-error-threshold', help='Error threshold for the CPU power models (in Watt)', type=float, default=2.0)
    parser.add_argument('--dram-error-threshold', help='Error threshold for the DRAM power models (in Watt)', type=float, default=2.0)

    # Debug options
    parser.add_argument('-T', '--dry-run', help='Dry run mode', action='store_true', default=False)
    parser.add_argument("-D", '--debug', help='Debug mode', action='store_true', default=False)

    return parser.parse_args()


def run_smartwatts(args, logger):
    """
    Run PowerAPI with the SmartWatts formula.
    :param args: CLI arguments namespace
    :param logger: Log level to use for the actors
    :return: Nothing
    """

    # Print configuration
    logger.info('SmartWatts version %s using PowerAPI version %s', smartwatts_version, powerapi_version)
    logger.info('CPU formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (args.cpu_rapl_ref_event, args.cpu_error_threshold))
    logger.info('DRAM formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (args.dram_rapl_ref_event, args.dram_error_threshold))

    # Reports pusher
    power_output_mongodb = MongoDB(args.mongodb_uri, args.mongodb_database, args.mongodb_powermeter_collection, None)
    power_report_pusher = PusherActor('power_report_pusher', PowerReport, power_output_mongodb)
    formula_output_mongodb = MongoDB(args.mongodb_uri, args.mongodb_database, args.mongodb_formula_collection, None)
    formula_report_pusher = PusherActor('formula_report_pusher', FormulaReport, formula_output_mongodb)

    # CPU topology information
    cpu_topology = CPUTopology(args.cpu_base_clock, args.cpu_ratio_min, args.cpu_ratio_base, args.cpu_ratio_max)

    # Sensor reports route table
    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(HWPCDepthLevel.SOCKET, primary=True))

    # CPU formula dispatcher
    def cpu_formula_factory(name: str, _):
        return SmartWattsFormulaActor(name,
                                      power_report_pusher,
                                      formula_report_pusher,
                                      FormulaScope.CPU,
                                      args.cpu_rapl_ref_event,
                                      args.cpu_error_threshold,
                                      cpu_topology)

    cpu_dispatcher = DispatcherActor('cpu_dispatcher', cpu_formula_factory, route_table)

    # DRAM formula dispatcher
    def dram_formula_factory(name: str, _):
        return SmartWattsFormulaActor(name,
                                      power_report_pusher,
                                      formula_report_pusher,
                                      FormulaScope.DRAM,
                                      args.dram_rapl_ref_event,
                                      args.dram_error_threshold,
                                      cpu_topology)

    dram_dispatcher = DispatcherActor('dram_dispatcher', dram_formula_factory, route_table)

    # Sensor reports puller
    input_mongodb = MongoDB(args.mongodb_uri, args.mongodb_database, args.mongodb_sensor_collection, HWPCModel(), stream_mode=True)
    report_filter = Filter()
    report_filter.filter(lambda msg: True, cpu_dispatcher)
    report_filter.filter(lambda msg: True, dram_dispatcher)
    puller = PullerActor('hwpc_report_puller', input_mongodb, report_filter)

    def term_handler(_, __):
        puller.join()
        cpu_dispatcher.join()
        dram_dispatcher.join()
        power_report_pusher.join()
        formula_report_pusher.join()
        exit(0)

    # TERM/INT signals handler
    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    # Actors supervision
    supervisor = Supervisor()
    try:
        supervisor.launch_actor(power_report_pusher)
        supervisor.launch_actor(formula_report_pusher)
        supervisor.launch_actor(cpu_dispatcher)
        supervisor.launch_actor(dram_dispatcher)
        supervisor.launch_actor(puller)
        logger.info('Actors initialized, SmartWatts is now running...')
    except zmq.error.ZMQError as exn:
        logger.error('Communication error, ZMQError code : ' + str(exn.errno) + ' reason : ' + exn.strerror)
        supervisor.kill_actors()
    except ActorInitError as exn:
        logger.error('Actor initialisation error, reason : ' + exn.message)
        supervisor.kill_actors()

    supervisor.join()


if __name__ == "__main__":
    ARGS = parse_cli_args()
    log_level = logging.INFO
    if ARGS.debug:
        log_level = logging.DEBUG

    LOGGER = logging.getLogger('main_logger')
    LOGGER.setLevel(log_level)
    LOGGER.addHandler(logging.StreamHandler())
    run_smartwatts(ARGS, LOGGER)
