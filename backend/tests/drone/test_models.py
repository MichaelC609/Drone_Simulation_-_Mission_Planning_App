from datetime import datetime
import uuid

import pytest
from pydantic import ValidationError

from drone.models import (
	DroneState,
	DroneStatusEnum,
	FlightModeEnum,
	Position,
	Velocity,
	validBatteryRange,
	validHeadingRange,
)


def test_position_defaults():
	position = Position()

	assert position.x == 0
	assert position.y == 0
	assert position.z == 0


def test_velocity_defaults():
	velocity = Velocity()

	assert velocity.vx == 0
	assert velocity.vy == 0
	assert velocity.vz == 0


def test_drone_state_defaults():
	drone_state = DroneState()

	assert isinstance(drone_state.id, uuid.UUID)
	assert isinstance(drone_state.position, Position)
	assert isinstance(drone_state.velocity, Velocity)
	assert drone_state.battery == 100
	assert drone_state.heading == 0
	assert drone_state.status == DroneStatusEnum.IDLE
	assert drone_state.flight_mode == FlightModeEnum.MANUAL
	assert isinstance(drone_state.timestamp, datetime)


def test_drone_state_defaults_are_isolated_instances():
	state_one = DroneState()
	state_two = DroneState()

	assert state_one.id != state_two.id
	assert state_one.position is not state_two.position
	assert state_one.velocity is not state_two.velocity


@pytest.mark.parametrize("battery", [0, 50, 100])
def test_valid_battery_range_accepts_boundary_values(battery):
	assert validBatteryRange(battery) == battery


@pytest.mark.parametrize("battery", [-0.1, 100.1])
def test_valid_battery_range_rejects_out_of_bounds_values(battery):
	with pytest.raises(ValueError):
		validBatteryRange(battery)


@pytest.mark.parametrize("heading", [0, 90, 359.999])
def test_valid_heading_range_accepts_boundary_values(heading):
	assert validHeadingRange(heading) == heading


@pytest.mark.parametrize("heading", [-1, 360])
def test_valid_heading_range_rejects_out_of_bounds_values(heading):
	with pytest.raises(ValueError):
		validHeadingRange(heading)


@pytest.mark.parametrize("battery", [-1, 101])
def test_drone_state_model_validation_rejects_invalid_battery(battery):
	with pytest.raises(ValidationError):
		DroneState(battery=battery)


@pytest.mark.parametrize("heading", [-0.001, 360])
def test_drone_state_model_validation_rejects_invalid_heading(heading):
	with pytest.raises(ValidationError):
		DroneState(heading=heading)


def test_drone_state_construction_from_nested_dicts():
	drone_state = DroneState(
		position={"x": 10.0, "y": -2.5, "z": 30.25},
		velocity={"vx": 1.5, "vy": 0.0, "vz": -0.2},
		battery=75,
		heading=180,
		status="ACTIVE",
		flight_mode="AUTONOMOUS",
	)

	assert drone_state.position == Position(x=10.0, y=-2.5, z=30.25)
	assert drone_state.velocity == Velocity(vx=1.5, vy=0.0, vz=-0.2)
	assert drone_state.status == DroneStatusEnum.ACTIVE
	assert drone_state.flight_mode == FlightModeEnum.AUTONOMOUS


def test_drone_state_construction_from_model_instances():
	position = Position(x=1, y=2, z=3)
	velocity = Velocity(vx=4, vy=5, vz=6)

	drone_state = DroneState(position=position, velocity=velocity)

	assert drone_state.position == position
	assert drone_state.velocity == velocity
