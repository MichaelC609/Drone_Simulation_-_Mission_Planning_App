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

from simulation.handlers import takeoff_handler


class _StubStateManager:
	def __init__(self, altitude=0.0):
		self.altitude = altitude
		self.status = DroneStatus.IDLE

	def getState(self):
		return types.SimpleNamespace(
			position=types.SimpleNamespace(z=self.altitude),
			status=self.status,
		)

	def updateState(self, update):
		if "position" in update and "z" in update["position"]:
			self.altitude = update["position"]["z"]
		if "status" in update:
			self.status = update["status"]


def _make_takeoff_command(target_altitude=10.0, takeoff_speed=2.0):
	return types.SimpleNamespace(
		payload=types.SimpleNamespace(
			target_altitude=target_altitude,
			takeoff_speed=takeoff_speed,
		)
	)


def test_takeoff_progress_one_tick():
	state_manager = _StubStateManager(altitude=0.0)
	command = _make_takeoff_command(target_altitude=10.0, takeoff_speed=2.0)

	assert state_manager.status == DroneStatus.IDLE

	completed = takeoff_handler.execute(command=command, state_manager=state_manager, dt=0.05)

	assert state_manager.altitude == pytest.approx(0.1)
	assert state_manager.status == DroneStatus.ACTIVE
	assert completed is False


def test_takeoff_completion_one_tick():
	state_manager = _StubStateManager(altitude=9.95)
	command = _make_takeoff_command(target_altitude=10.0, takeoff_speed=2.0)

	completed = takeoff_handler.execute(command=command, state_manager=state_manager, dt=0.05)

	assert state_manager.altitude == pytest.approx(10.0)
	assert completed is True
	assert state_manager.status == DroneStatus.ACTIVE