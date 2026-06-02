#################################################################################
# Models.py:                                                                    #    
#   Contains the infrastructure of the core models that define the main metrics #
#   and status of the drone                                                     #
#       Ex: Position, Velocity, DroneState, Flight_Mode, DroneState             #
#   Requirements: pip install pydantic                                          #
#################################################################################

from pydantic import BaseModel, Field, AfterValidator
from enum import Enum
from typing import Annotated
from datetime import datetime
import uuid

########### Validation Methods ###########
def validBatteryRange(batteryValue: int) -> int:
    if (batteryValue < 0) or (batteryValue > 100):
        raise ValueError(f"{batteryValue} is not a valid battery percentage")
    
    return batteryValue

def validHeadingRange(degreeValue: float) -> float:
    if (degreeValue < 0) or (degreeValue > 360):
        raise ValueError(f"{degreeValue} is not a valid degree range")
    
    return degreeValue

########### Model Classes ###########
class Position(BaseModel):
    #position for x-axis and y-axis along with flight altitude all in meters
    x: float = Field(default = 0)   
    y: float = Field(default = 0)
    z: float = Field(default = 0)

class Velocity(BaseModel):
    #velocity for x-axis and y-axis along with flight altitude measured in meters / second
    vx: float = Field(default = 0)
    vy: float = Field(default = 0)
    vz: float = Field(default = 0)

class DroneStatusEnum(str, Enum):
    IDLE = 'IDLE'
    ACTIVE = 'ACTIVE'
    LANDING = 'LANDING'
    ERROR = 'ERROR'

class FlightModeEnum(str, Enum):
    MANUAL = 'MANUAL'
    AUTONOMOUS = 'AUTONOMOUS'

class DroneState(BaseModel):
    id: uuid.UUID = Field(default_factory = uuid.uuid4)
    position: Position = Field(default_factory=Position)
    velocity: Velocity = Field(default_factory=Velocity)
    battery: Annotated[float, AfterValidator(validBatteryRange)] = Field(default = 100)
    heading: Annotated[float, AfterValidator(validHeadingRange)] = Field(default = 0)
    status: DroneStatusEnum = Field(default = DroneStatusEnum.IDLE)
    flight_mode: FlightModeEnum = Field(default = FlightModeEnum.MANUAL)
    timestamp: datetime = Field(default_factory=datetime.now)

