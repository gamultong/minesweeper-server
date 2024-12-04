from board.data import Point, Section, Tile, Tiles

DATA_PATH = "board/data/handler/internal/boarddata"

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


class BoardHandler:
    # sections[y][x]
    sections: dict[int, dict[int, Section]] = BOARD_DATA

    @staticmethod
    def fetch(start: Point, end: Point) -> Tiles:
        out = bytearray()

        for sec_y in range(start.y // Section.LENGTH, end.y // Section.LENGTH - 1, - 1):
            l = None
            for sec_x in range(start.x // Section.LENGTH, end.x // Section.LENGTH + 1):
                section = BoardHandler.sections[sec_y][sec_x]

                start_p = Point(
                    x=max(start.x, section.abs_x) - (section.abs_x),
                    y=min(start.y, section.abs_y + Section.LENGTH-1) - section.abs_y
                )
                end_p = Point(
                    x=min(end.x, section.abs_x + Section.LENGTH-1) - section.abs_x,
                    y=max(end.y, section.abs_y) - section.abs_y
                )

                fetched = section.fetch(start=start_p, end=end_p)

                x_gap, y_gap = (end_p.x - start_p.x + 1), (start_p.y - end_p.y + 1)
                if l == None:
                    l = [fetched.data[i*x_gap:(i+1)*x_gap] for i in range(y_gap)]
                    continue

                for i in range(y_gap):
                    l[i] += fetched.data[i*x_gap:(i+1)*x_gap]

            out += bytearray().join(l)

        return Tiles(data=out)

    def update_tile(p: Point, tile: Tile):
        tiles = Tiles(data=bytearray([tile.data]))

        sec_p = Point(x=p.x // Section.LENGTH, y=p.y // Section.LENGTH)
        section = BoardHandler.sections[sec_p.y][sec_p.x]

        section.update(data=tiles, start=p)

        # 지금은 안 해도 되긴 할텐데 일단 해 놓기
        BoardHandler.sections[sec_p.y][sec_p.x] = section

    @staticmethod
    def _debug():
        for y in BoardHandler.sections:
            for x in BoardHandler.sections[y]:
                print("=================================")
                print(f"Section x :", x)
                print(f"        y :", y)
                BoardHandler.sections[y][x]._debug()
