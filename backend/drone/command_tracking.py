#################################################################################
# command_tracking.py:                                                          #    
#   defines different status states for a command within its lifecycle          $
#       ex: rejected, success,queued, failed                                    #
#   contains necessary metadata for a given command within its lifecycle        #
#  Requirements:                                                                #
#       enum, uuid, pydantic, datetime                                          #
#################################################################################

#necessary imports
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field
from drone.commands import CommandTypeEnum
from datetime import datetime

#keeps track of different possible command states
class CommandStatusEnum(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

#keeps track of meta data for each command at a given time
class CommandRecord(BaseModel):
    command_id: UUID    #reuse existing UUID value from CommandBase
    command_type: CommandTypeEnum
    status: CommandStatusEnum = Field(default=CommandStatusEnum.QUEUED)
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None