#################################################################################
# command_queue.py:                                                             #    
#   The Data Structure responsible for storing drone commands before sending    #
#    them to the simulation engine                                              #
#################################################################################

from collections import deque

#Custom exception for empty queue operations
class EmptyQueueException(Exception):
    pass

#Implementation of the Deque Data Structure used to store Drone Commands
class CommandQueue:
    #constructor method -- initializes a valid empty queue
    def __init__(self):
        self._queue = deque()   #queue implementation is private to other components

    #adds a command to the back of the queue
    def enqueue(self, command):
        self._queue.append(command)

    #removes the oldest command from the front of the queue
    def dequeue(self):
        if self.isEmpty():
            raise EmptyQueueException("Queue is empty")
        
        return self._queue.popleft()

    #identifies and returns the command at the front of the queue
    def peek(self):
        if self.isEmpty():
            raise EmptyQueueException("Queue is empty")
        
        return self._queue[0]

    #returns true if the length of the queue is 0
    def isEmpty(self):
        if len(self._queue) > 0:
            return False
        
        return True

    #returns the length of the queue
    def size(self):
        return len(self._queue)

    