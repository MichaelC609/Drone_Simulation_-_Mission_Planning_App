##################################################################################
# api/routes/Simulation.py:                                                      #    
#   Constructs FastAPI Response model, passing in drone data such as position,   #             
#       velocity, simulation context & time, battery, etc                        #
#   Requirement: Fast API                                                        #
##################################################################################

from fastapi import APIRouter, Request, Body
from api.schemas import DroneStateResponse, CommandRequest, CommandResponse
from simulation.command_queue import CommandQueue

router = APIRouter(prefix="/simulation", tags=["simulation"])

@router.get("/state", response_model=DroneStateResponse)
async def get_simulation_state(request: Request):
    #retrieve the simulation context and current drone state
    sim_context = request.app.state.simulation_context
    drone_state = sim_context.state_manager.getState()
    sim_time = sim_context.simulation_engine.simulation_time

    #construct drone state response object
    drone_state_reponse = DroneStateResponse(
        position = drone_state.position,
        velocity = drone_state.velocity,
        droneStatus = drone_state.status,
        battery = drone_state.battery,
        simulation_time = sim_time
    )

    return drone_state_reponse

#POST method for submittting commands to API
@router.post("/commands", response_model=CommandResponse, status_code=202)
async def submit_command(request: Request, command: CommandRequest = Body(...)):
    sim_context = request.app.state.simulation_context

    #add validated command object to queue
    sim_context.command_queue.enqueue(command)

    #construct command response
    response_model = CommandResponse(
        command_id = command.id,
        command_type = command.command_type,
        status = "QUEUED",
        message = "Command accepted and queued for execution"
    )

    return response_model