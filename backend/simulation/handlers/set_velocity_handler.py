class SetVelocityHandler:
    @staticmethod
    def execute(command, state_manager, dt):
        velocity = {
            "vx": command.payload.vx,
            "vy": command.payload.vy,
            "vz": command.payload.vz,
        }
        state_manager.updateState({"velocity": velocity})
        return True
