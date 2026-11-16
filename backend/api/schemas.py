##################################################################################
# Schemas.py:                                                                    #    
#   Contains model information for exposing drone data to frontend via FastAPI.  #
#       Ex: Position, Velocity, Status, Battery, Simulation time.                #
#   Requirement: pydantic                                                        #
##################################################################################

from pydantic import BaseModel, Field
from drone.models import Position, Velocity, DroneStatusEnum, DroneState
from typing import Annotated, Union, Literal
from uuid import UUID
from pydantic import BaseModel, Field

from drone.commands import (
    TakeoffCommand,
    LandCommand,
    SetVelocityCommand,
    CommandTypeEnum
)

class DroneStateResponse(BaseModel):
    #import existing models
    position : Position
    velocity : Velocity
    droneStatus : DroneStatusEnum

    battery : float     #remaining battery
    simulation_time: float  #elapse time on simulation

CommandRequest = Annotated[
    Union[
        TakeoffCommand,
        LandCommand,
        SetVelocityCommand
    ],

    Field(discriminator="command_type")
]

class CommandResponse(BaseModel):
    command_id: UUID
    command_type: CommandTypeEnum
    status: str
    message: str