from .point import Point
from .section import Section

DATA_PATH = "board/internal/boarddata"

SECTION_1 = Section.from_str(Point(-1, 0), open(f"{DATA_PATH}/data1.txt", "r").read())
SECTION_2 = Section.from_str(Point(0, 0), open(f"{DATA_PATH}/data2.txt", "r").read())
SECTION_3 = Section.from_str(Point(-1, -1), open(f"{DATA_PATH}/data3.txt", "r").read())
SECTION_4 = Section.from_str(Point(0, -1), open(f"{DATA_PATH}/data4.txt", "r").read())

BOARD_DATA = \
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



class Board:
    # sections[y][x]
    sections:dict[int, dict[int, Section]] = BOARD_DATA

    @staticmethod
    def fetch(start: Point, end: Point):
        out = [bytearray() for _ in range(start.y - end.y + 1)]
        offset = 0
        fetched = None
        for sec_y in range(start.y // Section.LENGTH, end.y // Section.LENGTH - 1, - 1):
            for sec_x in range(start.x // Section.LENGTH, end.x // Section.LENGTH + 1):
                # TODO: 임시로 기존 맵 돌려쓰도록 만듦. **나중에 삭제**
                section = Board.sections[sec_y % -len(Board.sections)][sec_x % -len(Board.sections)]

                abs_sec_x = sec_x * Section.LENGTH
                abs_sec_y = sec_y * Section.LENGTH

                start_p = Point(
                    x=max(start.x, abs_sec_x) - (abs_sec_x),
                    y=min(start.y, abs_sec_y + Section.LENGTH-1) - abs_sec_y
                )
                end_p = Point(
                    x=min(end.x, abs_sec_x + Section.LENGTH-1) - abs_sec_x,
                    y=max(end.y, abs_sec_y) - abs_sec_y
                )
                
                fetched = section.fetch(start=start_p, end=end_p)
                
                for y in range(len(fetched)):
                    out[offset+y] += fetched[y]

            offset += len(fetched)

        return bytearray().join(out).decode("ascii")
    
    @staticmethod
    def _debug():
        for y in Board.sections:
            for x in Board.sections[y]:
                print("=================================")
                print(f"Section x :", x)
                print(f"        y :", y)
                Board.sections[y][x]._debug()