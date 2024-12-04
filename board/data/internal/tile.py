from dataclasses import dataclass
from cursor.data import Color
from .tile_exception import InvalidTileException


@dataclass
class Tile:
    is_open: bool
    is_mine: bool
    is_flag: bool
    color: Color | None
    number: int | None

    @property
    def data(self) -> int:
        d = 0b00000000

        d |= 0b10000000 if self.is_open else 0
        d |= 0b01000000 if self.is_mine else 0
        d |= 0b00100000 if self.is_flag else 0
        d |= self.number if self.number is not None else 0

        match self.color:
            case Color.RED | None:
                color_bits = 0
            case Color.YELLOW:
                color_bits = 1
            case Color.BLUE:
                color_bits = 2
            case Color.PURPLE:
                color_bits = 3

        d |= color_bits << 3

        return d

    @staticmethod
    def create(
        is_open: bool,
        is_mine: bool,
        is_flag: bool,
        color: Color | None,
        number: int | None
    ):
        if number and (number >= 8 or number < 0):
            raise InvalidTileException
        if is_mine and number:
            raise InvalidTileException
        if is_open and is_flag:
            raise InvalidTileException
        if is_flag and (color is None):
            raise InvalidTileException
        if (not is_flag) and (color is not None):
            raise InvalidTileException

        t = Tile(
            is_open=is_open,
            is_mine=is_mine,
            is_flag=is_flag,
            color=color,
            number=number
        )
        return t

    @staticmethod
    def from_int(b: int):
        is_open = bool(b & 0b10000000)
        is_mine = bool(b & 0b01000000)
        is_flag = bool(b & 0b00100000)

        color = extract_color(b) if is_flag else None
        number = extract_number(b) if not is_mine else None

        if is_open and is_flag:
            raise InvalidTileException()

        t = Tile(
            is_open=is_open,
            is_mine=is_mine,
            is_flag=is_flag,
            color=color,
            number=number
        )
        return t


def extract_color(b: int) -> Color:
    mask = 0b00011000
    match (b & mask) >> 3:
        case 0:
            return Color.RED
        case 1:
            return Color.YELLOW
        case 2:
            return Color.BLUE
        case 3:
            return Color.PURPLE


def extract_number(i: int) -> int | None:
    result = i & 0b00000111
    if result == 0:
        # 0은 None으로 반환
        return None
    return result
