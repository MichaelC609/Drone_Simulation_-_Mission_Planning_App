from drone import state_manager
from state_manager import StateManager
from drone import commands

def execute(command, state_manager, dt):
    #get current drone state
    currentState = StateManager.getState()

    #retrieve altitude
    altitude = currentState.position.z

    #retrieve target altitude and takeoff speed
    target_altitude = commands.Takeoff_Payload.target_altitude
    takeoff_speed = commands.Takeoff_Payload.takeoff_speed

    #compute altitude change and clamp new altitude
    altitude_delta = takeoff_speed * dt
    new_altitude = min((altitude + altitude_delta), target_altitude)

    #update state manager
    StateManager.updateState(new_altitude)

    #check for completion
    if new_altitude >= target_altitude:
        return True
    
    else:
        return False

