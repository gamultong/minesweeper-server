from board import Point
from dataclasses import dataclass
from .base_payload import Payload
from enum import Enum
class TilesEvent(str, Enum):
    FETCH_TILES = "fetch-tiles"
    TILES = "tiles"

@dataclass
class FetchTilesPayload(Payload):
    event = "fetch-tiles"
    start_x:int
    start_y:int
    end_x:int
    end_y:int

    @property
    def start_p(self):
        return Point(self.start_x, self.start_y)
    @property
    def end_p(self):
        return Point(self.end_x, self.end_y)

@dataclass
class TilesPayload(Payload):
    event = "tiles"
    start_x:int
    start_y:int
    end_x:int
    end_y:int
    tiles:str

    @property
    def start_p(self):
        return Point(self.start_x, self.start_y)
    @property
    def end_p(self):
        return Point(self.end_x, self.end_y)
    