#necessary imports
import sys
import importlib
from pathlib import Path

from simulation.simulation_engine import SimulationEngine
from api.simulation_runner import SimulationRunner
from api.simulation_context import SimulationContext

from drone.state_manager import StateManager
from simulation.command_queue import CommandQueue
from simulation.handler_registry import HandlerRegistry

import pytest
import asyncio

#required: pytest-asyncio


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if "models" not in sys.modules:
    sys.modules["models"] = importlib.import_module("drone.models")


def _build_context():
    return SimulationContext(
        state_manager=StateManager(),
        command_queue=CommandQueue(),
        handler_registry=HandlerRegistry(),
    )

def test_runner_start_creates_task():
    #setup simulation engine and runner
    context = _build_context()
    simulation_engine = context.simulation_engine
    simulation_runner = SimulationRunner(simulation_engine)

    #call start() and start a task
    simulation_runner.start()

    assert simulation_runner.task is not None
    assert simulation_runner.running == True

@pytest.mark.asyncio
async def test_runner_stop_cancels_task():
    #setup simulation engine and runner
    context = _build_context()
    simulation_engine = context.simulation_engine
    simulation_runner = SimulationRunner(simulation_engine)
    
    #verify task is running
    simulation_runner.start()
    assert simulation_runner.task is not None
    assert simulation_runner.running == True

    #execute stop() and verify task is cleared
    await simulation_runner.stop()
    assert simulation_runner.task is None

@pytest.mark.asyncio
async def test_simulation_time_advances():
    #create context, runner and engine
    context = _build_context()
    simulation_engine = context.simulation_engine
    simulation_runner = SimulationRunner(simulation_engine)

    #start task
    simulation_runner.start()

    await asyncio.sleep(0.1)

    #verify simulation time > 0
    assert simulation_engine.get_simulation_time() > 0

    #stop running task
    await simulation_runner.stop()

