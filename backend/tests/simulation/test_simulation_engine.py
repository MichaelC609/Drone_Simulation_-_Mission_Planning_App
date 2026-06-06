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


from drone.commands import CommandTypeEnum, TakeoffCommand, TakeoffPayload
from drone.state_manager import StateManager
from simulation.command_queue import CommandQueue
from simulation.handlers import takeoff_handler
from simulation.simulation_engine import SimulationEngine


class _TakeoffHandlerAdapter:
    def execute(self, command, state_manager, dt):
        takeoff_handler.commands.Takeoff_Payload = types.SimpleNamespace(
            target_altitude=command.payload.target_altitude,
            takeoff_speed=command.payload.takeoff_speed,
        )

        class _StateManagerShim:
            @staticmethod
            def getState():
                return state_manager.getState()

            @staticmethod
            def updateState(new_altitude):
                return state_manager.updateState({"position": {"z": new_altitude}})

        takeoff_handler.StateManager = _StateManagerShim

        return takeoff_handler.execute(command, state_manager, dt)


def test_end_to_end_takeoff_simulation_reaches_target_altitude():
    state_manager = StateManager()
    queue = CommandQueue()

    queue.enqueue(
        TakeoffCommand(
            payload=TakeoffPayload(target_altitude=1.0, takeoff_speed=1.0)
        )
    )

    handler_registry = {
        CommandTypeEnum.TAKEOFF: _TakeoffHandlerAdapter(),
    }

    engine = SimulationEngine(
        state_manager=state_manager,
        command_queue=queue,
        handler_registry=handler_registry,
        timestep=0.05,
    )

    while engine.active_command is not None or not queue.isEmpty():
        engine.tick()

    assert state_manager.getState().position.z == pytest.approx(1.0)
    assert engine.active_command is None

