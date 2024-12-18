import random
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

    # 맵의 각 끝단 섹션 위치
    max_x: int = 0
    min_x: int = 0
    max_y: int = 0
    min_y: int = 0

    @staticmethod
    def fetch(start: Point, end: Point) -> Tiles:
        # 반환할 데이터 공간 미리 할당
        out_width, out_height = (end.x - start.x + 1), (start.y - end.y + 1)
        out = bytearray(out_width * out_height)

        # TODO: 새로운 섹션과의 관계로 경계값이 바뀔 수 있음.
        # 이를 fetch 결과에 적용시킬 수 있도록 미리 다 만들어놓고 fetch를 시작해야 함.
        # 현재는 섹션이 메모리 내부 레퍼런스로 저장되기 때문에 이렇게 미리 받아놓고 할 수 있음.
        # 나중에는 다시 섹션을 가져와야 함.
        sections = []
        for sec_y in range(start.y // Section.LENGTH, end.y // Section.LENGTH - 1, - 1):
            for sec_x in range(start.x // Section.LENGTH, end.x // Section.LENGTH + 1):
                section = BoardHandler._get_or_create_section(sec_x, sec_y)
                sections.append(section)

        for section in sections:
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
    def get_random_open_position() -> Point:
        """
        전체 맵에서 랜덤한 열린 타일 위치를 하나 찾는다.
        섹션이 하나 이상 존재해야한다.
        """
        # 이미 방문한 섹션들
        visited = set()

        sec_x_range = (BoardHandler.min_x, BoardHandler.max_x)
        sec_y_range = (BoardHandler.min_y, BoardHandler.max_y)

        while True:
            rand_p = Point(
                x=random.randint(sec_x_range[0], sec_x_range[1]),
                y=random.randint(sec_y_range[0], sec_y_range[1])
            )

            if (rand_p.x, rand_p.y) in visited:
                continue

            visited.add((rand_p.x, rand_p.y))

            chosen_section = BoardHandler._get_section_or_none(rand_p.x, rand_p.y)
            if chosen_section is None:
                continue

            # 섹션 내부의 랜덤한 열린 타일 위치를 찾는다.
            inner_point = randomly_find_open_tile(chosen_section)
            if inner_point is None:
                continue

            open_point = Point(
                x=chosen_section.abs_x + inner_point.x,
                y=chosen_section.abs_y + inner_point.y
            )

            return open_point

    @staticmethod
    def _get_or_create_section(x: int, y: int) -> Section:
        if y not in BoardHandler.sections:
            BoardHandler.max_y = max(BoardHandler.max_y, y)
            BoardHandler.min_y = min(BoardHandler.min_y, y)

            BoardHandler.sections[y] = {}

        if x not in BoardHandler.sections[y]:
            BoardHandler.max_x = max(BoardHandler.max_x, x)
            BoardHandler.min_x = min(BoardHandler.min_x, x)

            new_section = Section.create(Point(x, y))

            # (x, y)
            delta = [
                (0, 1), (0, -1), (-1, 0), (1, 0),  # 상하좌우
                (-1, 1), (1, 1), (-1, -1), (1, -1),  # 좌상 우상 좌하 우하
            ]

            # 주변 섹션과 새로운 섹션의 인접 타일을 서로 적용시킨다.
            for dx, dy in delta:
                nx, ny = x+dx, y+dy
                neighbor = BoardHandler._get_section_or_none(nx, ny)
                # 주변 섹션이 없을 수 있음.
                if neighbor is None:
                    continue

                if dx != 0 and dy != 0:
                    neighbor.apply_neighbor_diagonal(new_section)
                elif dx != 0:
                    neighbor.apply_neighbor_horizontal(new_section)
                elif dy != 0:
                    neighbor.apply_neighbor_vertical(new_section)

                BoardHandler.sections[ny][nx] = neighbor

            BoardHandler.sections[y][x] = new_section

        return BoardHandler.sections[y][x]

    @staticmethod
    def _get_section_or_none(x: int, y: int) -> Section | None:
        if y in BoardHandler.sections and x in BoardHandler.sections[y]:
            return BoardHandler.sections[y][x]


def randomly_find_open_tile(section: Section) -> Point | None:
    """
    섹션 안에서 랜덤한 열린 타일 위치를 찾는다.
    시작 위치, 순회 방향(순방향, 역방향)의 순서를 무작위로 잡아 탐색한다.
    만약 열린 타일이 존재하지 않는다면 None.
    """

    # (증감값, 한계값)
    dirs = [(1, (Section.LENGTH ** 2) - 1), (-1, 0)]  # 순방향, 역방향
    random.shuffle(dirs)

    start = random.randint(0, (Section.LENGTH ** 2) - 1)

    for num, limit in dirs:
        for idx in range(start, limit + num, num):
            data = section.data[idx]

            tile = Tile.from_int(data)
            if not tile.is_open:
                continue

            # 열린 타일 찾음.
            x = idx % Section.LENGTH
            y = Section.LENGTH - (idx // Section.LENGTH) - 1

            return Point(x, y)
