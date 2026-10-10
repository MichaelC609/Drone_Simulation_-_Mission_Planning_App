###################################################################
#File: command_validator.py                                       #
#Purpose:                                                         #
#   Determines whether a command can execute given the drone's    #
#   current status(ie. Takeoff invalid if drone is active         #
#   or landing)                                                   #
###################################################################

#necessary imports
from drone.commands import CommandTypeEnum
from drone.models import DroneStatusEnum
from simulation.exceptions import InvalidCommandStateException

class CommandValidator:
    @staticmethod
    def validate(command, state_manager):
        #get current drone state
        current_state = state_manager.getState()

        #extract status and command type
        status = current_state.status
        command_type = command.command_type

        #check each valid command type & status -> invalid status = custom exception
        if command_type == CommandTypeEnum.LAND:
            if status != DroneStatusEnum.ACTIVE:
                #raise exception for invalid command for [status]
                raise InvalidCommandStateException(f"Cannot execute {command_type.value} while drone status is {status.value}") 

            return

        if command_type == CommandTypeEnum.TAKEOFF:
            if status != DroneStatusEnum.IDLE:
                #raise exception for invalid command for [status]
                raise InvalidCommandStateException(f"Cannot execute {command_type.value} while drone status is {status.value}") 

            return

        if command_type == CommandTypeEnum.SET_VELOCITY:
            if status != DroneStatusEnum.ACTIVE:
                #raise exception for invalid command for [status]
                raise InvalidCommandStateException(f"Cannot execute {command_type.value} while drone status is {status.value}") 

            return

        raise InvalidCommandStateException(
            f"Unsupported command type: {command_type}"
        )