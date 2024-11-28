from board import Point
from cursor import Color
from dataclasses import dataclass
from .base_payload import Payload
from enum import Enum


class NewConnEvent(str, Enum):
    NEW_CONN = "new-conn"
    NEARYBY_CURSORS = "nearby-cursors"
    CURSOR_APPEARED = "cursor-appeared"
    MY_CURSOR = "my-cursor"


@dataclass
class NewConnPayload(Payload):
    conn_id: str
    width: int
    height: int


@dataclass
class CursorPayload(Payload):
    position: Point
    pointer: Point | None
    color: Color


@dataclass
class CursorsPayload(Payload):
    cursors: list[CursorPayload]


class NewCursorPayload(CursorPayload):
    pass
