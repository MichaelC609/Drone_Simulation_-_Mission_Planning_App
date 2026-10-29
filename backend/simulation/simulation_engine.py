#################################################################################
# simulation_engine.py:                                                         #    
#   Responsible for the core logic and physics of the simulation engine         #
#   contains the methods controlling the tick, command and simulation logic     #
#################################################################################


import logging

from drone.commands import CommandTypeEnum
from simulation.command_validator import CommandValidator
from simulation.exceptions import InvalidCommandStateException

logger = logging.getLogger(__name__)


class SimulationEngine:
    #constructor method
    def __init__(self, state_manager, command_queue, handler_registry, physics_engine, dt):
        #injected dependencies
        self.state_manager = state_manager
        self.command_queue = command_queue
        self.handler_registry = handler_registry
        self.physics_engine = physics_engine
        
        self.active_command = None  
        self.simulation_time = 0.0  #measured in seconds
        self.dt = dt  #fixed timestep value

    def tick(self):
        skip_physics = False

        # Validate a command once, when it first leaves the queue.
        if self.active_command is None:
            if not self.command_queue.isEmpty():
                command = self.command_queue.dequeue()
                try:
                    CommandValidator.validate(command, self.state_manager)
                except InvalidCommandStateException as exc:
                    logger.warning(
                        "Rejected command %s: %s",
                        command.id,
                        exc,
                    )
                else:
                    self.active_command = command

        # Execute the active command without revalidating it on later ticks.
        if self.active_command is not None:
            command_type = self.active_command.command_type
            handler = self.handler_registry.get_handler(command_type)
            completed = handler.execute(
                self.active_command,
                self.state_manager,
                self.dt,
            )
            skip_physics = command_type in (
                CommandTypeEnum.TAKEOFF,
                CommandTypeEnum.LAND,
            )

            if completed:
                self.active_command = None

        if not skip_physics:
            self.physics_engine.update(
                self.state_manager,
                self.dt
            )

        self.simulation_time += self.dt

    def get_simulation_time(self):
        return self.simulation_time

    
