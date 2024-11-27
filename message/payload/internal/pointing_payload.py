from .parsable_payload import ParsablePayload
from .base_payload import Payload
from board import Point
from dataclasses import dataclass
from cursor import Color
from enum import Enum


class PointEvent(Enum):
    POINTING = "pointing"
    TRY_POINTING = "try-pointing"
    POINTING_RESULT = "pointing-result"
    POINTER_SET = "pointer-set"


@dataclass
class PointingPayload(Payload):
    position: ParsablePayload[Point]
    click_type: str


@dataclass
class TryPointingPayload(Payload):
    cursor_position: ParsablePayload[Point]
    new_pointer: ParsablePayload[Point]
    color: Color
    click_type: str


@dataclass
class PointingResultPayload(Payload):
    pointable: bool


@dataclass
class PointerSet(ParsablePayload):
    oringin_position: ParsablePayload[Point]
    new_position: ParsablePayload[Point]
    color: Color
