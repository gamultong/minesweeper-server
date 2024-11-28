from board import Point
from cursor import Color
from dataclasses import dataclass
from .base_payload import Payload
from enum import Enum


class MoveEvent(str, Enum):
    MOVING = "moving"
    MOVED = "moved"
    CHECK_MOVABLE = "check-movable"
    MOVABLE_RESULT = "movable-result"


@dataclass
class MovingPayload(Payload):
    position: Point


@dataclass
class MovedPayload(Payload):
    origin_position: Point
    new_position: Point
    color: Color


@dataclass
class CheckMovablePayload(Payload):
    position: Point


@dataclass
class MovableResultPayload(Payload):
    position: Point
    movable: bool
