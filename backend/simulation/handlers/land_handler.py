from drone import state_manager
from state_manager import StateManager
from drone import commands

def execute(command, state_manager, dt):
    #get current drone state
    currentState = state_manager.getState()

    #retrieve altitude
    altitude = currentState.position.z

    #retrieve target altitude and takeoff speed
    target_altitude = 0 #0m
    landing_speed = command.landing.landing_speed

    #compute altitude change and clamp new altitude
    altitude_delta = landing_speed * dt
    new_altitude = max((altitude - altitude_delta), target_altitude)

    #update state manager
    state_manager.updateState(new_altitude)

    #check for completion
    return new_altitude == target_altitude

