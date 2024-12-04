from .base_payload import Payload
from .parsable_payload import ParsablePayload
from board.data import Point, Tile
from dataclasses import dataclass


@dataclass
class YouDiedPayload():
    revive_at: str


@dataclass
class TileUpdatedPayload():
    position: ParsablePayload[Point]
    tile: ParsablePayload[Tile]


@dataclass
class TileStateChangedPayload():
    position: ParsablePayload[Point]
    tile: ParsablePayload[Tile]
