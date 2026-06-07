from drone.models import DroneStatusEnum
from simulation.battery_constants import BATTERY_DRAIN_RATE

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

    #calculate battery drain
    current_battery = currentState.battery
    new_battery = max(
        current_battery - (BATTERY_DRAIN_RATE["TAKEOFF"] * dt),
        0
    )

    #update state manager
    state_manager.updateState({"position": {"z": new_altitude}, "status": DroneStatusEnum.ACTIVE, "battery": new_battery})

    #check for completion
    return new_altitude >= target_altitude


