from tests.utils import cases
from board import Point, Section, BoardHandler

SECTION_1 = Section.from_str(Point(-1, 0), "asdfasdfasdfasdf")
SECTION_2 = Section.from_str(Point(0, 0), "1234123412341234")
SECTION_3 = Section.from_str(Point(-1, -1), "qwerqwerqwerqwer")
SECTION_4 = Section.from_str(Point(0, -1), "5678567856785678")

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
]


import unittest
class BoardHandlerTestCase(unittest.TestCase):
    def setUp(self):
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

    @cases(FETCH_CASE)
    def test_fetch(self, data, expect):
        start_p = data["start_p"]
        end_p = data["end_p"]

        data = BoardHandler.fetch(start_p, end_p)

        assert data == expect, f"{data} {expect}"     

if __name__ == "__main__":
    unittest.main()