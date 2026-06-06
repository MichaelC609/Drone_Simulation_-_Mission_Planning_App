import sys
import types
from pathlib import Path
import importlib

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

if str(BACKEND_ROOT) not in sys.path:
	sys.path.insert(0, str(BACKEND_ROOT))

if "models" not in sys.modules:
	sys.modules["models"] = importlib.import_module("drone.models")


if "state_manager" not in sys.modules:
	state_manager_module = types.ModuleType("state_manager")

	class _PlaceholderStateManager:
		pass

	state_manager_module.StateManager = _PlaceholderStateManager
	sys.modules["state_manager"] = state_manager_module


from simulation.handlers import takeoff_handler


class _StubStateManager:
	altitude = 0.0

	@staticmethod
	def getState():
		return types.SimpleNamespace(
			position=types.SimpleNamespace(z=_StubStateManager.altitude)
		)

	@staticmethod
	def updateState(new_altitude):
		_StubStateManager.altitude = new_altitude


def test_takeoff_progress_one_tick(monkeypatch):
	_StubStateManager.altitude = 0.0

	monkeypatch.setattr(takeoff_handler, "StateManager", _StubStateManager)
	monkeypatch.setattr(
		takeoff_handler.commands,
		"Takeoff_Payload",
		types.SimpleNamespace(target_altitude=10.0, takeoff_speed=2.0),
	)

	completed = takeoff_handler.execute(command=None, state_manager=None, dt=0.05)

	assert _StubStateManager.altitude == pytest.approx(0.1)
	assert completed is False


def test_takeoff_completion_one_tick(monkeypatch):
	_StubStateManager.altitude = 9.95

	monkeypatch.setattr(takeoff_handler, "StateManager", _StubStateManager)
	monkeypatch.setattr(
		takeoff_handler.commands,
		"Takeoff_Payload",
		types.SimpleNamespace(target_altitude=10.0, takeoff_speed=2.0),
	)

	completed = takeoff_handler.execute(command=None, state_manager=None, dt=0.05)

	assert _StubStateManager.altitude == pytest.approx(10.0)
	assert completed is True
