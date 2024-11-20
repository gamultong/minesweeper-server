from tests.utils import cases
from board import Point, Board
from .fixtures import setup_board

FETCH_CASE = \
[
    { # 가운데
        "data" : {
            "start_p" : Point(-2,1),
            "end_p" : Point(1, -2)
        },
        "expect": "df12df12er56er56"
    },
    { # 전체
        "data" : {
            "start_p" : Point(-4,3),
            "end_p"   : Point(3, -4)
        },
        "expect": "asdf1234asdf1234asdf1234asdf1234qwer5678qwer5678qwer5678qwer5678"
    },
    { # 한개
        "data" : {
            "start_p" : Point(0, 0),
            "end_p"   : Point(0, 0)
        },
        "expect": "1"
    },

    # out of bound
    # start_x <= end_x & start_y >= end_y
]


import unittest
class BoardTestCase(unittest.TestCase):
    def setUp(self):
        setup_board()

    @cases(FETCH_CASE)
    def test_fetch(self, data, expect):
        start_p = data["start_p"]
        end_p = data["end_p"]

        # print([[Board.sections[y][x].data for x in Board.sections[y]] for y in Board.sections])

        # Board._debug()

        data = Board.fetch(start_p, end_p)

        assert data == expect, f"{data} {expect}"     

if __name__ == "__main__":
    unittest.main()