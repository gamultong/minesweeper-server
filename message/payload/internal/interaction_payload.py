from .base_payload import Payload
from .parsable_payload import ParsablePayload
from board.data import Point, Tile
from dataclasses import dataclass
from enum import Enum


class InteractionEvent(Enum):
    YOU_DIED = "you-died"
    TILE_UPDATED = "tile-updated"
    TILE_STATE_CHANGED = "tile-state-changed"


@dataclass
class YouDiedPayload(Payload):
    revive_at: str


@dataclass
class TileUpdatedPayload(Payload):
    position: ParsablePayload[Point]
    tile: ParsablePayload[Tile]


@dataclass
class TileStateChangedPayload(Payload):
    position: ParsablePayload[Point]
    tile: ParsablePayload[Tile]
