#################################################################################
# simulation_engine.py:                                                         #    
#   Responsible for the core logic and physics of the simulation engine         #
#   contains the methods controlling the tick, command and simulation logic     #
#################################################################################


class SimulationEngine:
    #constructor method
    def __init__(self, state_manager, command_queue, handler_registry, timestep):
        #injected dependencies
        self.state_manager = state_manager
        self.command_queue = command_queue
        self.handler_registry = handler_registry
        
        self.active_command = None  
        self.simulation_time = 0.0  #measured in seconds
        self.dt = timestep  #fixed timestep value

    def tick(self):
        self.simulation_time += self.dt
        return self.simulation_time

    def get_simulation_time(self):
        return self.simulation_time

    

