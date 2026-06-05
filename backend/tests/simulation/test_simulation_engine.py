import pytest

from simulation.simulation_engine import SimulationEngine


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
