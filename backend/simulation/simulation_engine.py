#################################################################################
# simulation_engine.py:                                                         #    
#   Responsible for the core logic and physics of the simulation engine         #
#   contains the methods controlling the tick, command and simulation logic     #
#################################################################################


from backend.simulation.exceptions import HandlerNotFoundException
from simulation.handler_registry import HandlerRegistry
from drone.commands import CommandTypeEnum


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
        #acquire command
        if self.active_command is None:
            if not self.command_queue.isEmpty():
                self.active_command = self.command_queue.dequeue()

        command_type = None

        #execute command
        if self.active_command is not None:
            command_type = self.active_command.command_type
            handler = self.handler_registry.get_handler(
                command_type
            )
            
            completed = handler.execute(
                self.active_command,
                self.state_manager,
                self.dt
            )

            if completed:
                self.active_command = None

        if command_type not in (CommandTypeEnum.TAKEOFF, CommandTypeEnum.LAND):
            self.physics_engine.update(
                self.state_manager,
                self.dt
            )

        self.simulation_time += self.dt

    def get_simulation_time(self):
        return self.simulation_time

    

