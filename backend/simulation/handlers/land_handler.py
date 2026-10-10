from drone.models import DroneStatusEnum
from simulation.battery_constants import BATTERY_DRAIN_RATE

class LandHandler():
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

        #calculate battery drain
        current_battery = currentState.battery
        new_battery = max(
            current_battery - (BATTERY_DRAIN_RATE["LANDING"] * dt),
            0,
        )

        #update state manager
        status = DroneStatusEnum.IDLE if new_altitude == target_altitude else DroneStatusEnum.LANDING
        state_manager.updateState({"position": {"z": new_altitude}, "status": status, "battery": new_battery})

        #determine if landing is complete -> set status to IDLE and reset velocity
        completed = new_altitude == 0

        status = (
            DroneStatusEnum.IDLE if completed 
                else DroneStatusEnum.LANDING
        )

        updates = {
            "position": {"z": new_altitude},
            "status": status,
            "battery": new_battery
        }

        #reset velocity when landing completes
        if completed:
            updates["velocity"] = {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }

        state_manager.updateState(updates)

        return completed

