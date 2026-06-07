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


from drone.commands import (
    CommandTypeEnum,
    TakeoffCommand,
    TakeoffPayload,
    LandCommand,
    LandingPayload,
)
from drone.state_manager import StateManager
from simulation.command_queue import CommandQueue
from simulation.handlers import takeoff_handler, land_handler
from simulation.simulation_engine import SimulationEngine
from drone.models import DroneStatusEnum

################################
#       UNIT TESTS             #
################################

class _FunctionHandlerAdapter:
    def __init__(self, handler_func):
        self._handler_func = handler_func

    def execute(self, command, state_manager, dt):
        return self._handler_func(command, state_manager, dt)


################################
#       Integration TESTS      #
################################

def test_integration_takeoff_reaches_target_alt():
    state_manager = StateManager()
    queue = CommandQueue()

    queue.enqueue(
        TakeoffCommand(
            payload=TakeoffPayload(target_altitude=1.0, takeoff_speed=1.0)
        )
    )

    handler_registry = {
        CommandTypeEnum.TAKEOFF: _FunctionHandlerAdapter(takeoff_handler.execute),
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

    #verify battery and state
    state = state_manager.getState()
    assert state.status == DroneStatusEnum.ACTIVE
    assert state.battery < 100

def test_integration_landing_reaches_ground():
    #setup
    state_manager = StateManager()
    queue = CommandQueue()
    
    state_manager.updateState(
        {
            "position": {"z": 1.0},
            "status": DroneStatusEnum.ACTIVE
        }
    )

    queue.enqueue(
        LandCommand(payload=LandingPayload(landing_speed=1.0))
    )

    handler_registry = {
        CommandTypeEnum.LAND: _FunctionHandlerAdapter(land_handler.execute),
    }

    engine = SimulationEngine(
        state_manager=state_manager,
        command_queue=queue,
        handler_registry=handler_registry,
        timestep=0.05,
    )

    while engine.active_command is not None or not queue.isEmpty():
        engine.tick()

    assert state_manager.getState().position.z == pytest.approx(0.0)
    assert state_manager.getState().status == DroneStatusEnum.IDLE
    assert engine.active_command is None

    assert state_manager.getState().battery < 100


def test_multiple_commands_execute_in_sequence():
    state_manager = StateManager()
    queue = CommandQueue()

    queue.enqueue(
        TakeoffCommand(
            payload=TakeoffPayload(target_altitude=1.0, takeoff_speed=1.0)
        )
    )
    queue.enqueue(
        LandCommand(payload=LandingPayload(landing_speed=1.0))
    )

    handler_registry = {
        CommandTypeEnum.TAKEOFF: _FunctionHandlerAdapter(takeoff_handler.execute),
        CommandTypeEnum.LAND: _FunctionHandlerAdapter(land_handler.execute),
    }

    engine = SimulationEngine(
        state_manager=state_manager,
        command_queue=queue,
        handler_registry=handler_registry,
        timestep=0.05,
    )

    while engine.active_command is not None or not queue.isEmpty():
        engine.tick()

    state = state_manager.getState()
    assert state.position.z == pytest.approx(0.0)
    assert state.status == DroneStatusEnum.IDLE
    assert state.battery < 100
    assert engine.active_command is None
    assert queue.isEmpty() is True



