import pytest

from simulation.command_queue import CommandQueue, EmptyQueueException
from drone.commands import LandCommand, LandingPayload, TakeoffCommand, TakeoffPayload


def test_command_queue_initializes_empty():
	queue = CommandQueue()

	assert queue.isEmpty() is True
	assert queue.size() == 0


def test_dequeue_raises_when_queue_is_empty():
	queue = CommandQueue()

	with pytest.raises(EmptyQueueException, match="Queue is empty"):
		queue.dequeue()


def test_peek_raises_when_queue_is_empty():
	queue = CommandQueue()

	with pytest.raises(EmptyQueueException, match="Queue is empty"):
		queue.peek()


def test_enqueue_peek_and_dequeue_follow_fifo_order():
	queue = CommandQueue()
	first_command = TakeoffCommand(payload=TakeoffPayload(target_altitude=10, takeoff_speed=1.5))
	second_command = LandCommand(payload=LandingPayload())

	queue.enqueue(first_command)
	queue.enqueue(second_command)

	assert queue.isEmpty() is False
	assert queue.size() == 2
	assert queue.peek() == first_command
	assert queue.size() == 2
	assert queue.dequeue() == first_command
	assert queue.size() == 1
	assert queue.peek() == second_command
	assert queue.dequeue() == second_command
	assert queue.isEmpty() is True
	assert queue.size() == 0


def test_dequeue_reduces_queue_size():
	queue = CommandQueue()
	command = TakeoffCommand(payload=TakeoffPayload(target_altitude=12, takeoff_speed=2.0))

	queue.enqueue(command)

	assert queue.size() == 1
	assert queue.dequeue() == command
	assert queue.size() == 0
	assert queue.isEmpty() is True


def test_multiple_commands_maintain_fifo_order():
	queue = CommandQueue()
	first_command = TakeoffCommand(payload=TakeoffPayload(target_altitude=8, takeoff_speed=1.0))
	second_command = LandCommand(payload=LandingPayload(landing_speed=0.8))
	third_command = TakeoffCommand(payload=TakeoffPayload(target_altitude=20, takeoff_speed=3.0))

	queue.enqueue(first_command)
	queue.enqueue(second_command)
	queue.enqueue(third_command)

	assert queue.size() == 3
	assert queue.dequeue() == first_command
	assert queue.dequeue() == second_command
	assert queue.dequeue() == third_command
	assert queue.isEmpty() is True
