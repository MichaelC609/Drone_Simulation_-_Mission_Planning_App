def execute(command, state_manager, dt):
    #get current drone state
    currentState = state_manager.getState()

    #retrieve altitude
    altitude = currentState.position.z

    #retrieve target altitude and takeoff speed
    target_altitude = command.payload.target_altitude
    takeoff_speed = command.payload.takeoff_speed

    #compute altitude change and clamp new altitude
    altitude_delta = takeoff_speed * dt
    new_altitude = min((altitude + altitude_delta), target_altitude)

    #update state manager
    state_manager.updateState({"position": {"z": new_altitude}})

    #check for completion
    return new_altitude >= target_altitude

