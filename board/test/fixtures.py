from board import Board, Section, Point

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

def setup_board():
    Section.LENGTH = 4

    SECTION_1 = Section.from_str(Point(-1, 0), "asdfasdfasdfasdf")
    SECTION_2 = Section.from_str(Point(0, 0), "1234123412341234")
    SECTION_3 = Section.from_str(Point(-1, -1), "qwerqwerqwerqwer")
    SECTION_4 = Section.from_str(Point(0, -1), "5678567856785678")

    Board.sections = \
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
    