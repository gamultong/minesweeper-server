from models.section_model import Section, Point, SECTION_LENGTH

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

class MapHandler:
    # sections[y][x]
    sections:dict[int, dict[int, Section]] = {
        0: {
            0: SECTION_2,
            -1: SECTION_1
        },
        -1: {
            0: SECTION_4,
            -1: SECTION_3
        }
    }

    @staticmethod
    def fetch(start: Point, end: Point):
        out = [bytearray() for _ in range(start.y - end.y + 1)]
        offset = 0
        fetched = None
        for sec_y in range(start.y // SECTION_LENGTH, end.y // SECTION_LENGTH - 1, - 1):
            for sec_x in range(start.x // SECTION_LENGTH, end.x // SECTION_LENGTH + 1):
                section = MapHandler.sections[sec_y][sec_x]

                start_p = Point(
                    x=max(start.x, section.abs_x) - (section.abs_x),
                    y=min(start.y, section.abs_y + SECTION_LENGTH-1) - section.abs_y
                )
                end_p = Point(
                    x=min(end.x, section.abs_x + SECTION_LENGTH-1) - section.abs_x,
                    y=max(end.y, section.abs_y) - section.abs_y
                )
                
                fetched = section.fetch(start=start_p, end=end_p)
                
                for y in range(len(fetched)):
                    out[offset+y] += fetched[y]

            offset += len(fetched)

        return bytearray().join(out).decode("ascii")

                
                


                
            



