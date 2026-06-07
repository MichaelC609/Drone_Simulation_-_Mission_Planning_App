from datetime import datetime

from drone.models import DroneState, DroneStatusEnum
from drone.state_manager import StateManager


def test_state_manager_initializes_current_and_previous_state_as_independent_models():
	state_manager = StateManager()

	current_state = state_manager.getState()
	previous_state = state_manager.getPreviousState()

	assert isinstance(current_state, DroneState)
	assert isinstance(previous_state, DroneState)
	assert current_state == previous_state
	assert current_state is not previous_state


def test_update_state_preserves_previous_state_snapshot_and_returns_model():
	state_manager = StateManager()
	original_state = state_manager.getState().model_copy(deep=True)

	updated_state = state_manager.updateState(
		{
			"position": {"x": 12.5, "y": -3.0, "z": 50.0},
			"battery": 82.0,
			"status": "ACTIVE",
		}
	)

	previous_state = state_manager.getPreviousState()

	assert isinstance(updated_state, DroneState)
	assert previous_state == original_state
	assert previous_state is not original_state
	assert updated_state.position.x == 12.5
	assert updated_state.position.y == -3.0
	assert updated_state.position.z == 50.0
	assert updated_state.battery == 82.0
	assert updated_state.status == "ACTIVE"
	assert updated_state.timestamp >= original_state.timestamp


def test_reset_state_resets_current_and_previous_state():
	state_manager = StateManager()
	state_manager.updateState(
		{
			"battery": 45.0,
			"heading": 120.0,
			"flight_mode": "AUTONOMOUS",
		}
	)

	reset_state = state_manager.resetState()
	previous_state = state_manager.getPreviousState()

	assert isinstance(reset_state, DroneState)
	assert isinstance(previous_state, DroneState)
	assert reset_state.battery == 100
	assert reset_state.heading == 0
	assert reset_state.flight_mode == "MANUAL"
	assert reset_state.status == "IDLE"
	assert previous_state == reset_state
	assert previous_state is not reset_state


def test_update_state_refreshes_timestamp_with_current_value():
	state_manager = StateManager()
	previous_timestamp = state_manager.getState().timestamp

	updated_state = state_manager.updateState({"heading": 90.0})

	assert isinstance(updated_state.timestamp, datetime)
	assert updated_state.timestamp >= previous_timestamp


def test_update_state_accepts_enum_status_value():
	state_manager = StateManager()

	updated_state = state_manager.updateState({"status": DroneStatusEnum.ACTIVE})

	assert updated_state.status == DroneStatusEnum.ACTIVE
