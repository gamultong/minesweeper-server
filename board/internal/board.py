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
    sections: dict[int, dict[int, Section]] = BOARD_DATA

    @staticmethod
    def fetch(start: Point, end: Point):
        out = [bytearray() for _ in range(start.y - end.y + 1)]
        offset = 0
        fetched = None
        for sec_y in range(start.y // Section.LENGTH, end.y // Section.LENGTH - 1, - 1):
            for sec_x in range(start.x // Section.LENGTH, end.x // Section.LENGTH + 1):
                section = Board.sections[sec_y][sec_x]

                start_p = Point(
                    x=max(start.x, section.abs_x) - (section.abs_x),
                    y=min(start.y, section.abs_y + Section.LENGTH-1) - section.abs_y
                )
                end_p = Point(
                    x=min(end.x, section.abs_x + Section.LENGTH-1) - section.abs_x,
                    y=max(end.y, section.abs_y) - section.abs_y
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
