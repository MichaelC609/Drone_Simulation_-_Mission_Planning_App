##################################################################################
# Schemas.py:                                                                    #    
#   Contains model information for exposing drone data to frontend via FastAPI.  #
#       Ex: Position, Velocity, Status, Battery, Simulation time.                #
#   Requirement: pydantic
##################################################################################

from typing import Optional
from pydantic import BaseModel, Field
from ..drone.models import Position, Velocity, DroneStatusEnum, DroneState

class DroneStateResponse(BaseModel):
    #import existing models
    position = Position()
    velocity = Velocity()
    droneStatus = DroneStatusEnum()

    battery : float     #remaining battery
    simulation_time: float  #elapse time on simulation