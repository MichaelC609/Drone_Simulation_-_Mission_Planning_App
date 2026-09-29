import sys
import types
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

if str(BACKEND_ROOT) not in sys.path:
	sys.path.insert(0, str(BACKEND_ROOT))

from drone.models import DroneStatusEnum as DroneStatus
from simulation.handlers.land_handler import LandHandler
from simulation.battery_constants import BATTERY_DRAIN_RATE


class _StubStateManager:
	def __init__(self, altitude=0.0, status=DroneStatus.IDLE, battery=100.0):
		self.altitude = altitude
		self.status = status
		self.battery = battery

	def getState(self):
		return types.SimpleNamespace(
			position=types.SimpleNamespace(z=self.altitude),
			status=self.status,
			battery = self.battery
		)

	def updateState(self, update):
		if "position" in update and "z" in update["position"]:
			self.altitude = update["position"]["z"]
		if "status" in update:
			self.status = update["status"]
		if "battery" in update:
			self.battery = update["battery"]


def _make_land_command(landing_speed=1.0):
	return types.SimpleNamespace(
		payload=types.SimpleNamespace(landing_speed=landing_speed)
	)


def test_landing_progress_one_tick_sets_status_to_landing():
	state_manager = _StubStateManager(altitude=10.0, status=DroneStatus.ACTIVE)
	command = _make_land_command(landing_speed=1.0)

	completed = LandHandler.execute(command=command, state_manager=state_manager, dt=0.05)

	assert state_manager.altitude == pytest.approx(9.95)
	assert state_manager.status == DroneStatus.LANDING
	assert completed is False


def test_landing_completion_one_tick_sets_status_to_idle_and_completes():
	state_manager = _StubStateManager(altitude=0.02, status=DroneStatus.LANDING)
	command = _make_land_command(landing_speed=1.0)

	completed = LandHandler.execute(command=command, state_manager=state_manager, dt=0.05)

	assert state_manager.altitude == pytest.approx(0.0)
	assert state_manager.status == DroneStatus.IDLE
	assert completed is True


def test_landing_battery_drain():
	state_manager = _StubStateManager(
		altitude=10.0,
		status=DroneStatus.ACTIVE,
		battery=100.0,
	)
	command = _make_land_command(landing_speed=1.0)
	dt = 0.05

	completed = LandHandler.execute(command=command, state_manager=state_manager, dt=dt)

	expected_battery = 100.0 - (BATTERY_DRAIN_RATE["LANDING"] * dt)
	assert state_manager.battery == pytest.approx(expected_battery)
	assert state_manager.altitude == pytest.approx(9.95)
	assert state_manager.status == DroneStatus.LANDING
	assert completed is False

