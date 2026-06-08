import sys
import importlib
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]
SIMULATION_ROOT = Path(__file__).resolve().parents[2] / "simulation"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if str(SIMULATION_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULATION_ROOT))

if "models" not in sys.modules:
    sys.modules["models"] = importlib.import_module("drone.models")


from drone.commands import CommandTypeEnum
from simulation.handler_registry import (
    HandlerRegistry,
    HandlerNotFoundException,
    DuplicateHandlerRegistrationException,
)
from simulation.handlers.takeoff_handler import TakeoffHandler


def test_register_and_retrieve_handler():
    registry = HandlerRegistry()
    takeoff_handler = TakeoffHandler()

    registry.register(CommandTypeEnum.TAKEOFF, takeoff_handler)
    retrieved = registry.get_handler(CommandTypeEnum.TAKEOFF)

    assert retrieved is takeoff_handler
    assert isinstance(retrieved, TakeoffHandler)


def test_missing_handler_raises_exception():
    registry = HandlerRegistry()

    with pytest.raises(HandlerNotFoundException):
        registry.get_handler(CommandTypeEnum.TAKEOFF)


def test_duplicate_registration_raises_exception():
    registry = HandlerRegistry()
    first_takeoff_handler = TakeoffHandler()
    second_takeoff_handler = TakeoffHandler()

    registry.register(CommandTypeEnum.TAKEOFF, first_takeoff_handler)

    with pytest.raises(DuplicateHandlerRegistrationException):
        registry.register(CommandTypeEnum.TAKEOFF, second_takeoff_handler)


