from board.data import Point, Section, Tile, Tiles


def init_first_section() -> dict[int, dict[int, Section]]:
    section_0_0 = Section.create(Point(0, 0))

    tiles = section_0_0.fetch(Point(0, 0))

    t = Tile.from_int(tiles.data[0])
    t.is_open = True

    section_0_0.update(Tiles(data=[t.data]), Point(0, 0))

    return {0: {0: section_0_0}}


class BoardHandler:
    # sections[y][x]
    sections: dict[int, dict[int, Section]] = init_first_section()

    @staticmethod
    def fetch(start: Point, end: Point) -> Tiles:
        # 반환할 데이터 공간 미리 할당
        out_width, out_height = (end.x - start.x + 1), (start.y - end.y + 1)
        out = bytearray(out_width * out_height)

        for sec_y in range(start.y // Section.LENGTH, end.y // Section.LENGTH - 1, - 1):
            for sec_x in range(start.x // Section.LENGTH, end.x // Section.LENGTH + 1):
                section = BoardHandler._get_or_create_section(sec_x, sec_y)

                inner_start = Point(
                    x=max(start.x, section.abs_x) - (section.abs_x),
                    y=min(start.y, section.abs_y + Section.LENGTH-1) - section.abs_y
                )
                inner_end = Point(
                    x=min(end.x, section.abs_x + Section.LENGTH-1) - section.abs_x,
                    y=max(end.y, section.abs_y) - section.abs_y
                )

                fetched = section.fetch(start=inner_start, end=inner_end)

                x_gap, y_gap = (inner_end.x - inner_start.x + 1), (inner_start.y - inner_end.y + 1)

                # start로부터 떨어진 거리
                out_x = (section.abs_x + inner_start.x) - start.x
                out_y = start.y - (section.abs_y + inner_start.y)

                for row_num in range(y_gap):
                    out_idx = (out_width * (out_y + row_num)) + out_x
                    data_idx = row_num * x_gap

                    data = fetched.data[data_idx:data_idx+x_gap]
                    out[out_idx:out_idx+x_gap] = data

        return Tiles(data=out)

    @staticmethod
    def update_tile(p: Point, tile: Tile):
        tiles = Tiles(data=bytearray([tile.data]))

        sec_p = Point(x=p.x // Section.LENGTH, y=p.y // Section.LENGTH)
        section = BoardHandler.sections[sec_p.y][sec_p.x]

        inner_p = Point(
            x=p.x - section.abs_x,
            y=p.y - section.abs_y
        )

        section.update(data=tiles, start=inner_p)

        # 지금은 안 해도 되긴 할텐데 일단 해 놓기
        BoardHandler.sections[sec_p.y][sec_p.x] = section

    @staticmethod
    def _get_or_create_section(x: int, y: int) -> Section:
        if y not in BoardHandler.sections:
            BoardHandler.sections[y] = {}

        if x not in BoardHandler.sections[y]:
            new_section = Section.create(Point(x, y))
            # TODO: 주변 섹션과의 접경타일들 숫자 업데이트
            BoardHandler.sections[y][x] = new_section

        return BoardHandler.sections[y][x]
