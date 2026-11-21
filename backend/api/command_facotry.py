########################################################
#File: backend/api/command_factory.py                  #
#Description:                                          #
#   Serves as conversion layer between API and         #
#   simulation for command requests and responses      #
########################################################

#necessary imports
from api.schemas import TakeoffRequest, LandRequest, SetVelocityRequest
from drone.commands import TakeoffCommand, LandCommand, SetVelocityCommand

class CommandFactory():

    #########     create()   ################
    #   takes in a request object
    #   constructs internal command 
    #########################################
    @staticmethod
    def create(request):
        #create command based on command type

        #takeoff request -> takeoff command
        if isinstance(request, TakeoffRequest):
            takeoff_command = TakeoffCommand(payload = request.payload)
            return takeoff_command

        #land request -> land command
        elif isinstance(request, LandRequest):
            land_command = LandCommand(payload = request.payload)
            return land_command

        #setVelocity request -> setVelocity command
        elif isinstance(request, SetVelocityRequest):
            setVelocity_command = SetVelocityCommand(payload = request.payload)
            return setVelocity_command

        #if command is not a supported type -> raise Type Error
        else:
            raise TypeError(f"Invalid Command Type: {type(request).__name__}")