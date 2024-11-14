from typing import TypeVar, Generic
from dataclasses import dataclass
import json

class InvalidDataException(BaseException):
    def __init__(self, key, value, *args):
        self.msg = f"invaild {key} -> {value}"
        super().__init__(*args)

class MessageData():
    event:str

    @classmethod
    def from_dict(cls, dict: dict):
        kwargs = {}

        for key in dict:
            if not key in cls.__annotations__:
                raise InvalidDataException(key, dict[key])
            try:
                kwargs[key] = cls.__annotations__[key](dict[key])
            except:
                raise InvalidDataException(key, dict[key])

        return cls(**kwargs)

@dataclass
class FetchTilesData(MessageData):
    event = "fetch-tiles"
    start_x:int
    start_y:int
    end_x:int
    end_y:int

@dataclass
class TilesData(MessageData):
    event = "tiles"
    start_x:int
    start_y:int
    end_x:int
    end_y:int
    tiles:str

MESSAGE_DATA = TypeVar("message_data", bound=[FetchTilesData, TilesData])

class Message(Generic[MESSAGE_DATA]):
    def __init__(self, event:str, data:MESSAGE_DATA):
        self.event = event
        self.data = data

    def to_str(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True
            )
    
    @staticmethod
    def from_str(msg:str):
        decoded = json.loads(msg)

        event = decoded["event"]
        data = decode_data(event, decoded["data"])

        return Message(event=event, data=data)



def decode_data(event: str, data: dict):
    for sub_cls in MessageData.__subclasses__():
        if sub_cls.event == event:
            return sub_cls.from_dict(data)
