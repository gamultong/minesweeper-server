from board import Point
from cursor import Color
from dataclasses import dataclass
from .base_payload import Payload
from .parsable_payload import ParsablePayload
from enum import Enum


class NewConnEvent(str, Enum):
    NEW_CONN = "new-conn"
    CURSORS = "cursors"
    MY_CURSOR = "my-cursor"


@dataclass
class NewConnPayload(Payload):
    conn_id: str
    width: int
    height: int


@dataclass
class CursorPayload(Payload):
    position: ParsablePayload[Point]
    pointer: ParsablePayload[Point] | None
    color: Color


@dataclass
class CursorsPayload(Payload):
    cursors: list[CursorPayload]


class MyCursorPayload(CursorPayload):
    pass
