import re
from enum import Enum
from typing import Dict

from powerapi.formula import FormulaState, FormulaActor
from powerapi.pusher import PusherActor

from smartwatts.topology import CPUTopology


class SmartWattsFormulaScope(Enum):
    """
    Enum used to set the scope of the SmartWatts formula.
    """
    CPU = "cpu"
    DRAM = "dram"


class SmartWattsFormulaConfig:
    """
    Global config of the SmartWatts formula.
    """

    def __init__(self, scope: SmartWattsFormulaScope, reports_frequency: int, rapl_event: str, error_threshold: float, cpu_topology: CPUTopology):
        """
        Initialize a new formula config object.
        :param scope: Scope of the formula
        :param reports_frequency: Frequency at which the reports (in milliseconds)
        :param rapl_event: RAPL event to use as reference
        :param error_threshold: Error threshold (in Watt)
        :param cpu_topology: Topology of the CPU
        """
        self.scope = scope
        self.reports_frequency = reports_frequency
        self.rapl_event = rapl_event
        self.error_threshold = error_threshold
        self.cpu_topology = cpu_topology


class SmartWattsFormulaState(FormulaState):
    """
    State of the SmartWatts formula actor.
    """

    def __init__(self, actor: FormulaActor, pushers: Dict[str, PusherActor], config: SmartWattsFormulaConfig):
        """
        Initialize a new formula state object.
        :param actor: Actor of the formula
        :param pushers: Dictionary of available pushers
        :param config: Configuration of the formula
        """
        FormulaState.__init__(self, actor, pushers)
        self.config = config

        m = re.search(r'^\(\'(.*)\', \'(.*)\', \'(.*)\'\)$', actor.name)  # TODO: Need a better way to get these information
        self.dispatcher = m.group(1)
        self.sensor = m.group(2)
        self.socket = m.group(3)
