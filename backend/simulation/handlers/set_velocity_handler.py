class SetVelocityHandler:
    def execute(command, state_manager, dt):
        velocity = {
            "x": command.payload.vx,
            "y": command.payload.vy,
            "z": command.payload.vz,
        }
        state_manager.updateState({"velocity": velocity})
        return True
