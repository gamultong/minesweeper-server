from typing import Callable
from message import Message
from .exceptions import NoMatchingHandlerException

class EventPublisher:
    handler_dict: dict[str, Callable] = {}

    @staticmethod
    def add_handler(event: str):
        def wrapper(func: Callable):
            def func_wrapper(message: Message):
                func(message)

            EventPublisher.handler_dict[event] = func_wrapper
        
        return wrapper

    @staticmethod
    def remove_handler(event: str):
        if event in EventPublisher.handler_dict:
            del EventPublisher.handler_dict[event]
    
    @staticmethod
    def publish(message: Message):
        if message.event not in EventPublisher.handler_dict:
            raise NoMatchingHandlerException(message.event)

        handler = EventPublisher.handler_dict[message.event]

        handler(message)