from simulation.simulation_engine import SimulationEngine
from simulation.handlers.land_handler import LandHandler
from simulation.handlers.takeoff_handler import TakeoffHandler
from drone.commands import CommandTypeEnum

from api.simulation_runner import SimulationRunner

class SimulationContext:
    def __init__(self, state_manager, command_queue, handler_registry):
        self.state_manager = state_manager
        self.command_queue = command_queue
        self.handler_registry = handler_registry

        #instances of handler classes
        takeoff = TakeoffHandler()
        landing = LandHandler()

        #register handlers
        self.handler_registry.register(CommandTypeEnum.TAKEOFF, takeoff)
        self.handler_registry.register(CommandTypeEnum.LAND, landing)

        #create simulation engine with injected dependencies
        self.simulation_engine = SimulationEngine(
            self.state_manager,
            self.command_queue,
            self.handler_registry,
            dt=0.05
        )

        #create simulation runner
        self.simulation_runner = SimulationRunner(self.simulation_engine)