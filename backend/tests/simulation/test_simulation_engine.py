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
from simulation.handler_registry import HandlerRegistry
from simulation.handlers.takeoff_handler import TakeoffHandler
from simulation.handlers.land_handler import LandHandler
from simulation.simulation_engine import SimulationEngine
from drone.models import DroneStatusEnum

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

    handler_registry = HandlerRegistry()
    handler_registry.register(CommandTypeEnum.TAKEOFF, TakeoffHandler)

    engine = SimulationEngine(
        state_manager=state_manager,
        command_queue=queue,
        handler_registry=handler_registry,
        dt=0.05,
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

    handler_registry = HandlerRegistry()
    handler_registry.register(CommandTypeEnum.LAND, LandHandler)

    engine = SimulationEngine(
        state_manager=state_manager,
        command_queue=queue,
        handler_registry=handler_registry,
        dt=0.05,
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

    handler_registry = HandlerRegistry()
    handler_registry.register(CommandTypeEnum.TAKEOFF, TakeoffHandler)
    handler_registry.register(CommandTypeEnum.LAND, LandHandler)

    engine = SimulationEngine(
        state_manager=state_manager,
        command_queue=queue,
        handler_registry=handler_registry,
        dt=0.05,
    )

    while engine.active_command is not None or not queue.isEmpty():
        engine.tick()

    state = state_manager.getState()
    assert state.position.z == pytest.approx(0.0)
    assert state.status == DroneStatusEnum.IDLE
    assert state.battery < 100
    assert engine.active_command is None
    assert queue.isEmpty() is True


def test_simulation_time_advances_without_commands():
    state_manager = StateManager()
    queue = CommandQueue()

    handler_registry = HandlerRegistry()

    engine = SimulationEngine(
        state_manager=state_manager,
        command_queue=queue,
        handler_registry=handler_registry,
        dt=0.05,
    )

    assert engine.get_simulation_time() == pytest.approx(0.0)

    engine.tick()

    assert engine.get_simulation_time() == pytest.approx(0.05)



