from datetime import datetime
import uuid

import pytest
from pydantic import TypeAdapter, ValidationError

from drone.commands import (
	CommandBase,
	CommandTypeEnum,
	DroneCommand,
	LandCommand,
	LandingPayload,
	SetHeadingCommand,
	SetHeadingPayload,
	SetVelocityCommand,
	SetVelocityPayload,
	TakeoffCommand,
	TakeoffPayload,
	validAltitude,
	validHeadingRange,
	validLandingSpeed,
	validTakeoffValue,
)


def test_command_base_defaults():
	command_base = CommandBase()

	assert isinstance(command_base.id, uuid.UUID)
	assert isinstance(command_base.timestamp, datetime)


def test_command_base_defaults_are_isolated_instances():
	first = CommandBase()
	second = CommandBase()

	assert first.id != second.id
	assert first.timestamp != second.timestamp


def test_set_velocity_payload_defaults():
	payload = SetVelocityPayload()

	assert payload.vx == 0.0
	assert payload.vy == 0.0
	assert payload.vz == 0.0


def test_set_heading_payload_default_turn_rate():
	payload = SetHeadingPayload(target_heading=45)

	assert payload.target_heading == 45
	assert payload.turn_rate == 1.0


def test_landing_payload_default_speed():
	payload = LandingPayload()

	assert payload.landing_speed == 1.0


@pytest.mark.parametrize("takeoff_speed", [0.1, 1.0, 5.5])
def test_valid_takeoff_value_accepts_positive_values(takeoff_speed):
	assert validTakeoffValue(takeoff_speed) == takeoff_speed


@pytest.mark.parametrize("takeoff_speed", [0.0, -0.1])
def test_valid_takeoff_value_rejects_non_positive_values(takeoff_speed):
	with pytest.raises(ValueError):
		validTakeoffValue(takeoff_speed)


@pytest.mark.parametrize("altitude", [0.1, 10.0, 120.5])
def test_valid_altitude_accepts_positive_values(altitude):
	assert validAltitude(altitude) == altitude


@pytest.mark.parametrize("altitude", [0.0, -1.0])
def test_valid_altitude_rejects_non_positive_values(altitude):
	with pytest.raises(ValueError):
		validAltitude(altitude)


@pytest.mark.parametrize("landing_speed", [0.1, 1.0, 3.2])
def test_valid_landing_speed_accepts_positive_values(landing_speed):
	assert validLandingSpeed(landing_speed) == landing_speed


@pytest.mark.parametrize("landing_speed", [0.0, -2.0])
def test_valid_landing_speed_rejects_non_positive_values(landing_speed):
	with pytest.raises(ValueError):
		validLandingSpeed(landing_speed)


@pytest.mark.parametrize("heading", [0, 180, 359.999])
def test_valid_heading_range_accepts_boundary_values(heading):
	assert validHeadingRange(heading) == heading


@pytest.mark.parametrize("heading", [-0.001, 360])
def test_valid_heading_range_rejects_out_of_bounds_values(heading):
	with pytest.raises(ValueError):
		validHeadingRange(heading)


@pytest.mark.parametrize(
	"payload",
	[
		{"target_altitude": 20.0, "takeoff_speed": 2.5},
		TakeoffPayload(target_altitude=10, takeoff_speed=1.2),
	],
)
def test_takeoff_command_accepts_dict_and_model_payloads(payload):
	command = TakeoffCommand(payload=payload)

	assert command.command_type == CommandTypeEnum.TAKEOFF
	assert isinstance(command.payload, TakeoffPayload)


def test_takeoff_command_rejects_invalid_payload_values():
	with pytest.raises(ValidationError):
		TakeoffCommand(payload={"target_altitude": -5, "takeoff_speed": 2})


def test_land_command_defaults_and_payload():
	command = LandCommand(payload={})

	assert command.command_type == CommandTypeEnum.LAND
	assert command.payload == LandingPayload(landing_speed=1.0)


def test_set_velocity_command_accepts_payload_dict():
	command = SetVelocityCommand(payload={"vx": 3.0, "vy": -1.5, "vz": 0.2})

	assert command.command_type == CommandTypeEnum.SET_VELOCITY
	assert command.payload == SetVelocityPayload(vx=3.0, vy=-1.5, vz=0.2)


def test_set_heading_command_rejects_invalid_heading():
	with pytest.raises(ValidationError):
		SetHeadingCommand(payload={"target_heading": 360, "turn_rate": 1.5})


def test_set_heading_command_accepts_valid_payload():
	command = SetHeadingCommand(payload={"target_heading": 270, "turn_rate": 2.0})

	assert command.command_type == CommandTypeEnum.SET_HEADING
	assert command.payload == SetHeadingPayload(target_heading=270, turn_rate=2.0)


def test_drone_command_discriminated_union_parses_takeoff_command():
	adapter = TypeAdapter(DroneCommand)
	command = adapter.validate_python(
		{
			"command_type": "TAKEOFF",
			"payload": {"target_altitude": 15, "takeoff_speed": 1.8},
		}
	)

	assert isinstance(command, TakeoffCommand)
	assert command.payload.target_altitude == 15
	assert command.payload.takeoff_speed == 1.8


def test_drone_command_discriminated_union_rejects_unknown_command_type():
	adapter = TypeAdapter(DroneCommand)

	with pytest.raises(ValidationError):
		adapter.validate_python(
			{
				"command_type": "HOVER",
				"payload": {"target_altitude": 15, "takeoff_speed": 1.8},
			}
		)
