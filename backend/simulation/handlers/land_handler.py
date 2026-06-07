from drone.models import DroneStatusEnum

def execute(command, state_manager, dt):
    #get current drone state
    currentState = state_manager.getState()

    #retrieve altitude
    altitude = currentState.position.z

    #retrieve target altitude and landing speed
    target_altitude = 0 #0m
    landing_speed = command.payload.landing_speed

    #compute altitude change and clamp new altitude
    altitude_delta = landing_speed * dt
    new_altitude = max((altitude - altitude_delta), target_altitude)

    #update state manager
    status = DroneStatusEnum.IDLE if new_altitude == target_altitude else DroneStatusEnum.LANDING
    state_manager.updateState({"position": {"z": new_altitude}, "status": status})

    #check for completion
    return new_altitude == target_altitude

