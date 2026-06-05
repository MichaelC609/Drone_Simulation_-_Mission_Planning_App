import pytest

from simulation.command_queue import CommandQueue, EmptyQueueException


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
	first_command = {"command_type": "TAKEOFF", "payload": {"target_altitude": 10}}
	second_command = {"command_type": "LAND", "payload": {}}

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
