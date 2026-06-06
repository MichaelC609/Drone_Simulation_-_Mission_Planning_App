import pytest

from simulation.simulation_engine import SimulationEngine
from simulation.exceptions import HandlerNotFoundException

from simulation.handlers.takeoff_handler import TakeoffHandler
from simulation.handlers.land_handler import LandHandler
from drone.commands import CommandTypeEnum

from commands import (
    TakeoffCommand,
    TakeoffPayload
)

@pytest.fixture
def handler_registry():

    return {
        CommandTypeEnum.TAKEOFF: TakeoffHandler,
        CommandTypeEnum.LAND: LandHandler
    }

class MockQueue:
	def __init__(self):
		self.commands = []

	def enqueue(self, command):
		self.commands.append(command)

	def dequeue(self):
		self.commands.pop(0)

	def isEmpty(self):
		return len(self.commands) == 0
	
def test_takeoff_command_executes_and_completes(
    handler_registry
):

    queue = MockQueue()

    command = TakeoffCommand(
        command_type="TAKEOFF",
        payload=TakeoffPayload(
            altitude=10,
            speed=2
        )
    )

    queue.enqueue(command)

    engine = SimulationEngine(
        state_manager=object(),
        command_queue=queue,
        handler_registry=handler_registry,
        timestep=0.05
    )

    engine.tick()

    assert engine.active_command is None

    assert engine.simulation_time == pytest.approx(
        0.05
    )

def test_tick_without_commands_advances_time():

    queue = MockQueue()

    engine = SimulationEngine(
        state_manager=object(),
        command_queue=queue,
        handler_registry={},
        timestep=0.05
    )

    engine.tick()

    assert engine.simulation_time == pytest.approx(
        0.05
    )

def test_missing_handler_raises_exception():

    queue = MockQueue()

    command = TakeoffCommand(
        command_type="TAKEOFF",
        payload=TakeoffPayload(
            altitude=10,
            speed=2
        )
    )

    queue.enqueue(command)

    engine = SimulationEngine(
        state_manager=object(),
        command_queue=queue,
        handler_registry={},
        timestep=0.05
    )

    with pytest.raises(
        HandlerNotFoundException
    ):
        engine.tick()

def test_constructor_initializes_default_time_and_active_command():
	engine = SimulationEngine(
		state_manager=object(),
		command_queue=object(),
		handler_registry=object(),
		timestep=0.05,
	)

	assert engine.simulation_time == 0.0
	assert engine.active_command is None


def test_tick_increases_time_by_timestep():
	engine = SimulationEngine(
		state_manager=object(),
		command_queue=object(),
		handler_registry=object(),
		timestep=0.05,
	)

	engine.tick()

	assert engine.simulation_time == pytest.approx(0.05)


def test_three_ticks_result_in_point_fifteen_seconds():
	engine = SimulationEngine(
		state_manager=object(),
		command_queue=object(),
		handler_registry=object(),
		timestep=0.05,
	)

	engine.tick()
	engine.tick()
	engine.tick()

	assert engine.simulation_time == pytest.approx(0.15)

