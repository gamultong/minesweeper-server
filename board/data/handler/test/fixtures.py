from board.data import Section, Point
from board.data.handler import BoardHandler

"""
 3   a s d f 1 2 3 4
 2   a s d f 1 2 3 4
 1   a s d f 1 2 3 4
 0   a s d f 1 2 3 4
-1   q w e r 5 6 7 8
-2   q w e r 5 6 7 8
-3   q w e r 5 6 7 8
-4   q w e r 5 6 7 8
   
    -4-3-2-1 0 1 2 3
"""


def setup_board_fake():
    Section.LENGTH = 4

    SECTION_1 = Section.from_str(Point(-1, 0), "asdfasdfasdfasdf")
    SECTION_2 = Section.from_str(Point(0, 0), "1234123412341234")
    SECTION_3 = Section.from_str(Point(-1, -1), "qwerqwerqwerqwer")
    SECTION_4 = Section.from_str(Point(0, -1), "5678567856785678")

    BoardHandler.sections = \
        {
            0: {
                0: SECTION_2,
                -1: SECTION_1
            },
            -1: {
                0: SECTION_4,
                -1: SECTION_3
            }
        }


def setup_board():
    """
    /docs/example-map-state.png
    """
    Section.LENGTH = 4

    tile_state_1 = bytearray([
        0b00000000, 0b00000000, 0b00000000, 0b00000000,
        0b00000001, 0b00000001, 0b00000001, 0b00000000,
        0b10000001, 0b01110000, 0b00000001, 0b00000000,
        0b10000001, 0b00000001, 0b00000001, 0b00000000
    ])
    tile_state_2 = bytearray([
        0b00000001, 0b00000010, 0b00000010, 0b00000001,
        0b00000001, 0b01000000, 0b01000000, 0b00000001,
        0b00000001, 0b00000010, 0b10000010, 0b10000001,
        0b00000001, 0b00100001, 0b10000001, 0b10000000
    ])
    tile_state_3 = bytearray([
        0b00000001, 0b01000000, 0b10000010, 0b10000001,
        0b10000001, 0b10000001, 0b10000011, 0b01101000,
        0b10000000, 0b10000000, 0b10000010, 0b01000000,
        0b11000000, 0b10000000, 0b10000001, 0b00000001
    ])
    tile_state_4 = bytearray([
        0b10000001, 0b00111001, 0b00000001, 0b00000001,
        0b00000011, 0b00000010, 0b01000000, 0b00000001,
        0b00000011, 0b01000000, 0b00000010, 0b00000001,
        0b00000010, 0b00000001, 0b00000001, 0b00000000
    ])

    BoardHandler.sections = \
        {
            0: {
                0: Section(Point(0, 0), tile_state_1),
                -1: Section(Point(-1, 0), tile_state_2)
            },
            -1: {
                0: Section(Point(0, -1), tile_state_4),
                -1: Section(Point(-1, -1), tile_state_3)
            }
        }
