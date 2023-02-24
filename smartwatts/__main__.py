# Copyright (c) 2022, INRIA
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
from typing import Dict

from powerapi import __version__ as powerapi_version
from powerapi.backend_supervisor import BackendSupervisor
from powerapi.dispatcher import RouteTable

from powerapi.cli import ConfigValidator
from powerapi.cli.tools import store_true, CommonCLIParser
from powerapi.cli.generator import ReportModifierGenerator, PullerGenerator, PusherGenerator
from powerapi.exception import PowerAPIException
from powerapi.report import HWPCReport, PowerReport
from powerapi.dispatch_rule import HWPCDispatchRule, HWPCDepthLevel
from powerapi.filter import Filter
from powerapi.actor import InitializationException

from smartwatts import __version__ as smartwatts_version
from smartwatts.report import FormulaReport
from smartwatts.smartwatts_dispatcher_actor import SmartWattsDispatcherActor
from smartwatts.smartwatts_formula_actor import SmartWattsFormulaActor, SmartWattsFormulaScope, SmartWattsFormulaConfig
from smartwatts.topology import CPUTopology


def generate_smartwatts_parser():
    """
    Construct and returns the SmartWatts cli parameters parser.
    :return: SmartWatts cli parameters parser
    """
    parser = CommonCLIParser()

    # Formula control parameters
    parser.add_argument('disable-cpu-formula', help='Disable CPU formula', flag=True, type=bool, default=False,
                        action=store_true)
    parser.add_argument('disable-dram-formula', help='Disable DRAM formula', flag=True, type=bool, default=False,
                        action=store_true)

    # Formula RAPL reference event
    parser.add_argument('cpu-rapl-ref-event', help='RAPL event used as reference for the CPU power models',
                        default='RAPL_ENERGY_PKG')
    parser.add_argument('dram-rapl-ref-event', help='RAPL event used as reference for the DRAM power models',
                        default='RAPL_ENERGY_DRAM')

    # CPU topology information
    parser.add_argument('cpu-tdp', help='CPU TDP (in Watts)', type=int, default=125)
    parser.add_argument('cpu-base-clock', help='CPU base clock (in MHz)', type=int, default=100)
    parser.add_argument('cpu-frequency-min', help='CPU minimal frequency (in MHz)', type=int, default=100)
    parser.add_argument('cpu-frequency-base', help='CPU base frequency (in MHz)', type=int, default=2300)
    parser.add_argument('cpu-frequency-max', help='CPU maximal frequency (In MHz, with Turbo-Boost)', type=int,
                        default=4000)

    # Formula error threshold
    parser.add_argument('cpu-error-threshold', help='Error threshold for the CPU power models (in Watts)', type=float,
                        default=2.0)
    parser.add_argument('dram-error-threshold', help='Error threshold for the DRAM power models (in Watts)', type=float,
                        default=2.0)

    # Sensor information
    parser.add_argument('sensor-report-sampling-interval',
                        help='The frequency with which measurements are made (in milliseconds)', type=int, default=1000)

    # Learning parameters
    parser.add_argument('learn-min-samples-required',
                        help='Minimum amount of samples required before trying to learn a power model', type=int,
                        default=10)
    parser.add_argument('learn-history-window-size',
                        help='Size of the history window used to keep samples to learn from', type=int, default=60)
    parser.add_argument('real-time-mode', help='Pass the wait for reports from 4 ticks to 1', type=bool, default=False)
    return parser


def filter_rule(_):
    """
    Rule of filter. Here none
    """
    return True


def setup_formula_actor(be_supervisor: BackendSupervisor, global_configuration: Dict, route_table: RouteTable,
                        report_filter: Filter, cpu_topology: CPUTopology, formula_pushers: Dict,
                        power_pushers: Dict, rapl_event: str, error_threshold: int, dispatcher_name: str,
                        device_id: str):
    """
    Setup CPU formula actor.
    :param be_supervisor: Actor supervisor
    :param global_configuration: Global configuration
    :param route_table: Reports routing table
    :param report_filter: Reports filter
    :param cpu_topology: CPU topology information
    :param power_pushers: Power Reports pushers
    :param formula_pushers: Formula Reports pushers
    :param rapl_event: RAPL event associated with the Dispatcher
    :param error_threshold: Error threshold related to Formulas managed by the Dispatcher
    :param dispatcher_name: Dispatcher Name
    :param device_id: Id of the device related to the Dispatcher
    """
    formula_config = SmartWattsFormulaConfig(scope=SmartWattsFormulaScope.CPU,
                                             reports_frequency=global_configuration['sensor-report-sampling-interval'],
                                             rapl_event=rapl_event,
                                             error_threshold=error_threshold,
                                             cpu_topology=cpu_topology,
                                             min_samples_required=global_configuration['learn-min-samples-required'],
                                             history_window_size=global_configuration['learn-history-window-size'],
                                             real_time_mode=global_configuration['real-time-mode'])

    dispatcher = SmartWattsDispatcherActor(name=dispatcher_name, formula_init_function=SmartWattsFormulaActor,
                                           power_pushers=power_pushers, formula_pushers=formula_pushers,
                                           route_table=route_table, device_id=device_id,
                                           formula_config=formula_config, level_logger=logging.getLogger().level)

    be_supervisor.launch_actor(dispatcher)

    report_filter.filter(filter_rule, dispatcher)


def run_smartwatts(args) -> BackendSupervisor:
    """
    Run PowerAPI with the SmartWatts formula.
    :param args: CLI arguments namespace
    :param logger: Logger to use for the actors
    """
    global_configuration = args

    logging.info('SmartWatts version %s using PowerAPI version %s', smartwatts_version, powerapi_version)

    if global_configuration['disable-cpu-formula'] and global_configuration['disable-dram-formula']:
        logging.error('You need to enable at least one formula')
        return None

    route_table = RouteTable()
    route_table.dispatch_rule(HWPCReport, HWPCDispatchRule(HWPCDepthLevel.SOCKET, primary=True))

    cpu_topology = CPUTopology(tdp=global_configuration['cpu-tdp'],
                               freq_bclk=global_configuration['cpu-base-clock'],
                               ratio_min=global_configuration['cpu-frequency-min'],
                               ratio_base=global_configuration['cpu-frequency-base'],
                               ratio_max=global_configuration['cpu-frequency-max'])

    report_filter = Filter()

    report_modifier_list = ReportModifierGenerator().generate(global_configuration)

    be_supervisor = BackendSupervisor(global_configuration['stream'])  # Supervisor(args['verbose'], args['actor_system'])

    def term_handler(_, __):
        logging.info('SmartWatts is shutting down...')
        be_supervisor.kill_actors()
        sys.exit(0)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)
    try:
        logging.info('Starting SmartWatts actors...')

        pusher_generator = PusherGenerator()
        pusher_generator.add_report_class('FormulaReport', FormulaReport)
        pushers_info = pusher_generator.generate(global_configuration)
        formula_pushers = {}
        power_pushers = {}

        for pusher_name in pushers_info:
            pusher = pushers_info[pusher_name]

            if pusher.state.report_model == PowerReport:
                be_supervisor.launch_actor(pusher)
                power_pushers[pusher_name] = pusher
            elif pusher.state.report_model == FormulaReport:
                be_supervisor.launch_actor(pusher)
                formula_pushers[pusher_name] = pusher
            else:
                raise InitializationException("Pusher parameters : Provide supported report type as model for pusher")

        logging.info('CPU formula is %s' % ('DISABLED' if global_configuration['disable-cpu-formula'] else 'ENABLED'))
        if not global_configuration['disable-cpu-formula']:
            logging.info('CPU formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (
                global_configuration['cpu-rapl-ref-event'], global_configuration['cpu-error-threshold']))
            setup_formula_actor(be_supervisor=be_supervisor, global_configuration=global_configuration,
                                route_table=route_table, report_filter=report_filter, cpu_topology=cpu_topology,
                                formula_pushers=formula_pushers, power_pushers=power_pushers,
                                device_id='cpu', rapl_event=global_configuration['cpu-rapl-ref-event'],
                                error_threshold=global_configuration['cpu-error-threshold'],
                                dispatcher_name='cpu_dispatcher')

            logging.info(
                'DRAM formula is %s' % ('DISABLED' if global_configuration['disable-dram-formula'] else 'ENABLED'))
        if not global_configuration['disable-dram-formula']:
            logging.info('DRAM formula parameters: RAPL_REF=%s ERROR_THRESHOLD=%sW' % (
                global_configuration['dram-rapl-ref-event'], global_configuration['dram-error-threshold']))
            setup_formula_actor(be_supervisor=be_supervisor, global_configuration=global_configuration,
                                route_table=route_table, report_filter=report_filter, cpu_topology=cpu_topology,
                                formula_pushers=formula_pushers, power_pushers=power_pushers,
                                device_id='dram', rapl_event=global_configuration['dram-rapl-ref-event'],
                                error_threshold=global_configuration['dram-error-threshold'],
                                dispatcher_name='dram_dispatcher')

        pullers_info = PullerGenerator(report_filter=report_filter, report_modifier_list=report_modifier_list,
                                       ).generate(global_configuration)
        for puller_name in pullers_info:
            puller = pullers_info[puller_name]
            be_supervisor.launch_actor(puller)
    except InitializationException as exn:
        logging.error('Actor initialization error: ' + exn.msg)
        be_supervisor.kill_actors()
        sys.exit(-1)
    except PowerAPIException as exp:
        logging.error("PowerException error: %s", exp)
        be_supervisor.kill_actors()
        sys.exit(-1)

    logging.info('SmartWatts is now running...')
    return be_supervisor


class SmartWattsConfigValidator(ConfigValidator):
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
        if 'cpu-frequency-base' in config:
            config['cpu-frequency-base'] = int(config['cpu-frequency-base'] / 100)
        if 'cpu-frequency-min' in config:
            config['cpu-frequency-min'] = int(config['cpu-frequency-min'] / 100)
        if 'cpu-frequency-max' in config:
            config['cpu-frequency-max'] = int(config['cpu-frequency-max'] / 100)

        return True


def get_config():
    """
    Get he config from the cli args
    """
    parser = generate_smartwatts_parser()
    return parser.parse()


if __name__ == "__main__":

    conf = get_config()
    if not SmartWattsConfigValidator.validate(conf):
        sys.exit(-1)
    logging.basicConfig(level=logging.DEBUG if conf['verbose'] else logging.INFO)
    logging.captureWarnings(True)

    logging.debug(str(conf))
    supervisor = run_smartwatts(conf)

    while supervisor.are_all_actors_alive():
        pass

    supervisor.join()
    sys.exit(0)
