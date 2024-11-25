from board import Point
from cursor import Color
from dataclasses import dataclass
from .base_payload import Payload
from enum import Enum


class NewConnEvent(str, Enum):
    NEW_CONN = "new-conn"
    NEARYBY_CURSORS = "nearby-cursors"
    CURSOR_APPEARED = "cursor-appeared"


@dataclass
class NewConnPayload():
    conn_id: str
    width: int
    height: int


@dataclass
class CursorPayload():
    position_x: int
    position_y: int
    point_x: int
    point_y: int
    color: Color


@dataclass
class NearbyCursorPayload():
    cursors: list[CursorPayload]


class CursorAppearedPayload(CursorPayload):
    pass
