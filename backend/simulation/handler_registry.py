from .exceptions import DuplicateHandlerRegistrationException, HandlerNotFoundException

class HandlerRegistry:
    #constructor method
    def __init__(self):
        self._handlers = {}

    #add handler to dictionary
    def register(self, command_type, handler):
        #if command already present
        if command_type in self._handlers:
            raise DuplicateHandlerRegistrationException()
        
        #store handler
        self._handlers[command_type] = handler

    #retrieve handler based on command type
    def get_handler(self, command_type):
        if command_type not in self._handlers:
            raise HandlerNotFoundException()
        
        return self._handlers[command_type]
    
