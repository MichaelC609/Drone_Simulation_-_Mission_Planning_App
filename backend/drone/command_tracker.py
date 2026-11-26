#################################################################################
# command_tracker.py:                                                           #    
#   Responsible for controlling command registration and status updates between #
#       state transitions, taking in metadata about the command                 #
#   Requirements:                                                               #
#       uuid, datetime, /drone, copy                                            #
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


    #mark a command's state as running once it is queued and ready
    def mark_running(self, command_id: UUID) -> None:
        #retrieve command record from dict -> raise key error if doesn't exist
        command_record = self._get_internal_record(command_id)

        #validate transition and set status to running + started_at to current time
        self._validate_transitions(command_record.status, CommandStatusEnum.RUNNING)
        command_record.status = CommandStatusEnum.RUNNING
        command_record.started_at = datetime.now()


    #private helper method to retrieve internal record
    def _get_internal_record(self, command_id: UUID) -> CommandRecord:
        #retrieve record
        command_record = self._records.get(command_id)

        #if key exists -> return : else -> raise KeyError
        if command_record is None:
            raise KeyError(f"{command_id} does not exist in records")

        return command_record

    #marks a command as being completed
    def mark_completed(self, command_id: UUID) -> None:
        #retrieve record
        command_record = self._get_internal_record(command_id)

        #validate command's transition to COMPLETED status
        self._validate_transitions(command_record.status, CommandStatusEnum.COMPLETED)

        #update status and finished_at time
        command_record.status = CommandStatusEnum.COMPLETED
        command_record.finished_at = datetime.now()

    #indicates that a command has failed during execution
    def mark_failed(self, command_id: UUID, reason: str) -> None:
        #retrieve record
        command_record = self._get_internal_record(command_id)

        #validate command's transition to FAILED status
        self._validate_transitions(command_record.status, CommandStatusEnum.FAILED)

        #update status and finished_at time
        command_record.status = CommandStatusEnum.FAILED
        command_record.finished_at = datetime.now()

        command_record.error_message = reason

    #indicates that a command has failed validation before execution
    def mark_rejected(self, command_id: UUID, reason: str) -> None:
        #retrieve record
        command_record = self._get_internal_record(command_id)

        #validate command's transiiton to REJECTED status
        self._validate_transitions(command_record.status, CommandStatusEnum.REJECTED)

        #update status, finished_at and add error message
        command_record.status = CommandStatusEnum.REJECTED
        command_record.finished_at = datetime.now()

        command_record.error_message = reason



