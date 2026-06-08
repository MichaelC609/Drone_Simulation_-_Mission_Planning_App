import sys
import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if "models" not in sys.modules:
    sys.modules["models"] = importlib.import_module("drone.models")


from api.simulation_context import SimulationContext
from drone.commands import CommandTypeEnum
from drone.state_manager import StateManager
from simulation.command_queue import CommandQueue
from simulation.handler_registry import HandlerRegistry
from simulation.handlers.takeoff_handler import TakeoffHandler
from simulation.handlers.land_handler import LandHandler


def _build_context():
    return SimulationContext(
        state_manager=StateManager(),
        command_queue=CommandQueue(),
        handler_registry=HandlerRegistry(),
    )


def test_context_creates_all_dependencies():
    context = _build_context()

    assert context.state_manager is not None
    assert context.command_queue is not None
    assert context.handler_registry is not None
    assert context.simulation_engine is not None
    assert context.simulation_runner is not None


def test_handlers_are_registered():
    context = _build_context()

    takeoff_handler = context.handler_registry.get_handler(CommandTypeEnum.TAKEOFF)
    land_handler = context.handler_registry.get_handler(CommandTypeEnum.LAND)

    assert isinstance(takeoff_handler, TakeoffHandler)
    assert isinstance(land_handler, LandHandler)


def test_engine_uses_context_dependencies():
    context = _build_context()

    assert context.simulation_engine.state_manager is context.state_manager
    assert context.simulation_engine.command_queue is context.command_queue
    assert context.simulation_engine.handler_registry is context.handler_registry
