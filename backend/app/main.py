####################################################
#backend/app/main.py:                              #
#   responsible for main logic of                  #
#   backend and api integration(fastapi)           #
####################################################

#necessary imports
from fastapi import FastAPI
from contextlib import asynccontextmanager
from drone.state_manager import StateManager
from simulation.command_queue import CommandQueue
from simulation.handler_registry import HandlerRegistry
from api.simulation_context import SimulationContext

####################################################
#lifespan():                                       #
#   takes in app as argument                       #
#   Passes appropriate instances into simulation   #
#   context                                        #
####################################################

@asynccontextmanager
async def lifespan(app):
    #create instances for simulation context
    state_manager = StateManager()
    command_queue = CommandQueue()
    handler_registry = HandlerRegistry()

    #pass three instances into simulation context
    simulation_context = SimulationContext(
        state_manager, 
        command_queue, 
        handler_registry
    )

    #store context and call start() to begin simulation contetx
    app.state.simulation_context = simulation_context
    simulation_context.simulation_runner.start()

    try:
        yield

    finally:
        await simulation_context.simulation_runner.stop()

app = FastAPI(
    title = "Drone Simulation API",
    description = "REST API for controlling and monitoring a drone simuulation",
    version = "0.1.0",
    lifespan = lifespan
)