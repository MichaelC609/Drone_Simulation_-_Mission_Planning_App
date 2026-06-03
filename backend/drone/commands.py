#################################################################################
# commands.py:                                                                  #    
#   Contians the pydantic models for command types and classes                  #
#       Ex: TAKEOFF, SetVelocity, LAND                                          #
#   Requirements: pip install pydantic                                          #
#################################################################################

#necessary imports for Pydantic and field generation
from pydantic import AfterValidator, BaseModel, Field
from enum import Enum
from typing import Annotated, Literal, Union
import uuid
from datetime import datetime

########### Validation Methods ###########
def validTakeoffValue(takeoffSpeed: float) -> float:
    if takeoffSpeed <= 0.0:
        raise ValueError(f"{takeoffSpeed} is not a valid takeoff speed")
    
    return takeoffSpeed
    
def validAltitude(altitudeValue: float) -> float: 
    if altitudeValue <= 0.0:
        raise ValueError(f"{altitudeValue} is not a valid altitude")
    
    return altitudeValue
    
def validLandingSpeed(landingSpeed: float) -> float:
    if landingSpeed <= 0.0:
        raise ValueError(f"{landingSpeed} is not a valid landing speed")
    
    return landingSpeed
    
def validHeadingRange(degreeValue: float) -> float:
    if (degreeValue < 0) or (degreeValue >= 360):
        raise ValueError(f"{degreeValue} is not a valid degree range")
    
    return degreeValue

def validTurnRate(turnRate: float) -> float:
    if turnRate <= 0.0:
        raise ValueError(f"{turnRate} is not a valid turn rate speed")
    
    return turnRate


###### Main Model sub classes ######
class CommandTypeEnum(str, Enum):
    TAKEOFF = 'TAKEOFF'
    LAND = 'LAND'
    SET_VELOCITY = 'SET VELOCITY'
    SET_HEADING = 'SET HEADING'

###### Payload base classes ######
class Payload(BaseModel):
    pass

class SetVelocityPayload(Payload):
    vx: float = Field(default = 0.0)
    vy: float = Field(default = 0.0)
    vz: float = Field(default = 0.0)

class SetHeadingPayload(Payload):
    target_heading: Annotated[float, AfterValidator(validHeadingRange)]
    turn_rate: Annotated[float, AfterValidator(validTurnRate)] = Field(default = 1.0)

class TakeoffPayload(Payload):
    target_altitude: Annotated[float, AfterValidator(validAltitude)]
    takeoff_speed: Annotated[float, AfterValidator(validTakeoffValue)]

class LandingPayload(Payload):
    landing_speed: Annotated[float, AfterValidator(validLandingSpeed)] = Field(default = 1.0)


###### Typed command classes (Option B) ######
class CommandBase(BaseModel):
    id: uuid.UUID = Field(default_factory = uuid.uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)


class TakeoffCommand(CommandBase):
    command_type: Literal[CommandTypeEnum.TAKEOFF] = CommandTypeEnum.TAKEOFF
    payload: TakeoffPayload


class LandCommand(CommandBase):
    command_type: Literal[CommandTypeEnum.LAND] = CommandTypeEnum.LAND
    payload: LandingPayload


class SetVelocityCommand(CommandBase):
    command_type: Literal[CommandTypeEnum.SET_VELOCITY] = CommandTypeEnum.SET_VELOCITY
    payload: SetVelocityPayload


class SetHeadingCommand(CommandBase):
    command_type: Literal[CommandTypeEnum.SET_HEADING] = CommandTypeEnum.SET_HEADING
    payload: SetHeadingPayload


# Discriminated union: command_type selects exactly one command/payload pairing.
DroneCommand = Annotated[
    Union[TakeoffCommand, LandCommand, SetVelocityCommand, SetHeadingCommand],
    Field(discriminator='command_type')
]

# Backward-compatible aliases for older naming in existing call sites.
Set_Velocity_Payload = SetVelocityPayload
Set_Heading_Payload = SetHeadingPayload
Takeoff_Payload = TakeoffPayload
Landing_Payload = LandingPayload
