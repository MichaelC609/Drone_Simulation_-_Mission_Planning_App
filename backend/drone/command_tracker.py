#################################################################################
# command_tracker.py:                                                           #    
#   Responsible for controlling command registration and status updates between #
#       state transitions, taking in metadata about the command                 #
#################################################################################

#necessary imports
from uuid import UUID
from datetime import datetime
from drone.commands import DroneCommand
from drone.command_tracking import CommandStatusEnum
from drone.command_tracking import CommandRecord
import copy

class CommandTracker():
    #define dictionary containing valid command state enum values
    _allowed_transitions: dict[CommandStatusEnum, set[CommandStatusEnum]] = {
                CommandStatusEnum.QUEUED: {CommandStatusEnum.RUNNING, CommandStatusEnum.REJECTED},
                CommandStatusEnum.COMPLETED: set(),
                CommandStatusEnum.FAILED: set(),
                CommandStatusEnum.REJECTED: set(), 
                CommandStatusEnum.RUNNING: {CommandStatusEnum.COMPLETED, CommandStatusEnum.FAILED}
            }

    #initialize empty dictionary for command records
    def __init__(self):
        self._records: dict[UUID, CommandRecord] = {}

    #creates and stores command in record when submitted
    def register(self, command : DroneCommand) -> None:
        #raise value error if UUID exists in dictionary
        if command.id in self._records:
            raise ValueError(f"{command.id} already in Records")

        #if command isn't in dictionary -> create a command record
        else:
            command_record = CommandRecord(
                command_id = command.id, 
                command_type = command.command_type, 
                created_at = command.timestamp, 
            )

            self._records[command.id] = command_record

    #retrieve copy of associated command record given command unique id
    def get_record(self, command_id: UUID) -> CommandRecord | None:
        #retrieve record
        dict_record = self._records.get(command_id)

        #if key exists -> return copy of record
        if dict_record is not None:
            #returns copy of associated record
            return copy.deepcopy(dict_record)  

        else:
            return None    #returns None

    #determines whether a command is allowed to transition to its requested state
    #   based on its current state
    def _validate_transitions(self, current_status: CommandStatusEnum, new_status: CommandStatusEnum ) -> None:
        #retrieve and validate transition for current status
        valid_transitions = self._allowed_transitions.get(current_status, set())

        if new_status in valid_transitions:
            return 

        else:
            raise ValueError(f"{new_status} is not a valid transition state for {current_status}")




