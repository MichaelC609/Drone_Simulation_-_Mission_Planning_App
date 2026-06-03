#################################################################################
# state_manager.py:                                                             #    
#   Contains the interface responsible for creating and updating drone state    #
#   Uses a Python class with a constructor and class methods following an       #
#       OOP approach                                                            #
#   Ex: create_default_state(), getCurrentState(), getPreviousState()           #
#   Requirements:                                                               #
#################################################################################

#necessary imports
from models import DroneState
from datetime import datetime

class StateManager: 
    def __init__(self):
        self.current_state = self.create_default_state()
        self.previous_state = self.current_state.model_copy(deep=True)

    #function to merge previous json object with updated json state object
    def merge_curr_and_prev_states(self, original, updated):
        for key, value in updated.items():
            if (
                key in original
                and isinstance(original[key], dict)
                and isinstance(value, dict)
            ):
                self.merge_curr_and_prev_states(original[key], value)
            else:
                original[key] = value

        return original


    def create_default_state(self):
        return DroneState()
    
    def resetState(self):
        self.current_state = self.create_default_state()
        self.previous_state = self.current_state.model_copy(deep=True)
        return self.current_state
    
    def getState(self):
        return self.current_state

    def getPreviousState(self):
        return self.previous_state
    
    def updateState(self, update):
        # Preserve previous state and convert current state model to dict via Pydantic.
        self.previous_state = self.current_state.model_copy(deep=True)
        current_state_dict = self.current_state.model_dump(mode="python")

        newState = self.merge_curr_and_prev_states(current_state_dict, update)
        newState["timestamp"] = datetime.now()
        self.current_state = DroneState.model_validate(newState)
        return self.current_state

    
