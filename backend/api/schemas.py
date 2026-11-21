##################################################################################
# Schemas.py:                                                                    #    
#   Contains model information for exposing drone data to frontend via FastAPI.  #
#       Ex: Position, Velocity, Status, Battery, Simulation time.                #
#   Requirement: pydantic                                                        #
##################################################################################

from pydantic import BaseModel, Field, ConfigDict
from drone.models import Position, Velocity, DroneStatusEnum
from typing import Annotated, Union, Literal
from uuid import UUID

from drone.commands import (
    CommandTypeEnum,
    TakeoffPayload,
    LandingPayload,
    SetVelocityPayload
)

class DroneStateResponse(BaseModel):
    #import existing models
    position : Position
    velocity : Velocity
    droneStatus : DroneStatusEnum

    battery : float     #remaining battery
    simulation_time: float  #elapse time on simulation


class CommandResponse(BaseModel):
    command_id: UUID
    command_type: CommandTypeEnum
    status: str
    message: str

class TakeoffRequest(BaseModel):
    command_type: Literal[CommandTypeEnum.TAKEOFF] = CommandTypeEnum.TAKEOFF
    payload: TakeoffPayload
    model_config = ConfigDict(extra="forbid")

class LandRequest(BaseModel):
    command_type: Literal[CommandTypeEnum.LAND] = CommandTypeEnum.LAND
    payload: LandingPayload
    model_config = ConfigDict(extra="forbid")

class SetVelocityRequest(BaseModel):
    command_type: Literal[CommandTypeEnum.SET_VELOCITY] = CommandTypeEnum.SET_VELOCITY
    payload: SetVelocityPayload
    model_config = ConfigDict(extra="forbid")

CommandRequest = Annotated[
    Union[
        TakeoffRequest,
        LandRequest,
        SetVelocityRequest
    ],

    Field(discriminator="command_type")
]