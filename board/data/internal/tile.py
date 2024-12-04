from dataclasses import dataclass
from cursor.data import Color
from .tile_exception import InvalidTileException


@dataclass
class Tile:
    data: int
    is_open: bool
    is_mine: bool
    is_flag: bool
    color: Color | None
    number: int | None

    def __init__(self, data):
        self.data = data
        self.is_open = int_to_is_open(data)
        self.is_mine = int_to_is_mine(data)
        self.is_flag = int_to_is_flag(data)
        self.color = int_to_color(data)
        self.number = int_to_number(data)

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

        match color:
            case None:
                color_to_int = 0
            case Color.RED:
                color_to_int = 0
            case Color.YELLOW:
                color_to_int = 1
            case Color.BLUE:
                color_to_int = 2
            case Color.PURPLE:
                color_to_int = 3

        data = is_open << 7
        data |= is_mine << 6
        data |= is_flag << 5
        data |= color_to_int << 3
        data |= number if number != None else 0

        tile = Tile(
            data=data,
        )
        return tile

    @staticmethod
    def from_int(b: int):
        tile = Tile(
            data=b
        )

        if tile.is_open and tile.is_flag:
            raise InvalidTileException()

        if tile.is_open and tile.is_flag:
            raise InvalidTileException()

        return tile


def int_to_is_open(i: int):
    b = 0b10000000
    return bool(i & b)


def int_to_is_mine(i: int):
    b = 0b01000000
    return bool(i & b)


def int_to_is_flag(i):
    b = 0b00100000
    return bool(i & b)


def int_to_color(i):
    if not int_to_is_flag(i):
        return None

    b = 0b00011000
    match (i & b) >> 3:
        case 0:
            return Color.RED
        case 1:
            return Color.YELLOW
        case 2:
            return Color.BLUE
        case 3:
            return Color.PURPLE


def int_to_number(i):
    if int_to_is_mine(i):
        return None
    # 0이면 None
    if (0b00000111 & i):
        return (0b00000111 & i)
