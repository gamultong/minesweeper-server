from __future__ import annotations
from typing import Callable, Generic
from message import Message
from .exceptions import NoMatchingReceiverException
from message.internal.message import EVENT_TYPE
from uuid import uuid4

class Receiver(Generic[EVENT_TYPE]):
    receiver_dict:dict[str, Receiver] = {}

    def __init__(self, func, event):
        self.func:Callable[[Message[EVENT_TYPE]], None] = func
        self.event:str = event
        self.id:str = self.__get_uuid()
        Receiver.receiver_dict[self.id] = self

    def __get_uuid(self):
        while (id:=uuid4().hex) in Receiver.receiver_dict:
            pass
        return id
    
    def remove(self):
        if self.id not in Receiver.receiver_dict:
            return False
        del Receiver.receiver_dict[self.id]
        return True

    @staticmethod
    def get_receiver(id: str) -> Receiver|None:
        if id not in Receiver.receiver_dict:
            return None
        return Receiver.receiver_dict[id]
    
    def __call__(self, msg:Message[EVENT_TYPE]):
        return self.func(msg)

class EventBroker: 
    event_dict: dict[str, list[str]] = {}

    @staticmethod
    def add_receiver(event: str):
        def wrapper(func: Callable):
            receiver = Receiver(func, event)
            if event not in EventBroker.event_dict:
                EventBroker.event_dict[event] = []

            EventBroker.event_dict[event].append(receiver.id)

            return receiver
        return wrapper

    @staticmethod
    def remove_receiver(receiver: Receiver):
        if not (removed := receiver.remove()):
            return

        receivers = EventBroker.event_dict[receiver.event]
        receivers.remove(receiver.id)

        if len(EventBroker.event_dict[receiver.event]) == 0:
            del EventBroker.event_dict[receiver.event]

    @staticmethod
    def publish(message: Message):
        if message.event not in EventBroker.event_dict:
            raise NoMatchingReceiverException(message.event)

        receiver_ids = EventBroker.event_dict[message.event]
        for id in receiver_ids:
            receiver = Receiver.get_receiver(id)
            receiver(message)

        