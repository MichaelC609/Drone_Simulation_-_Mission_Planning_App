class PhysicsEngine:
    def update(state_manager, dt):
        #retrieve current drone state
        currentState = state_manager.getState()

        #get current position
        currentPos = currentState.position

        #get current velocity
        currentVelocity = currentState.velocity

        #calculate displacement for current tick -> d = v x dt
        dx = currentVelocity.x * dt
        dy = currentVelocity.y * dt
        dz = currentVelocity.z * dt

        #calculate new posiiton for current tick -> current pos + delta position
        new_pos_x = currentPos.x + dx
        new_pos_y = currentPos.y + dy
        new_pos_z = max(currentPos.z + dz, 0)
        
        newPosition = {
            "x": new_pos_x,
            "y": new_pos_y,
            "z": new_pos_z
        }

        state_manager.updateState({
            "position": newPosition
        })
