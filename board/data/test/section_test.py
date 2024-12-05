import unittest
from tests.utils import cases
from board.data import Section, Point, Tile, Tiles


# 테스트를 위해 Section.LENGTH를 4로 설정
Section.LENGTH = 4

# hex는 문자 2개 사용하기 때문에 2번 반복
EXAPMLE_SECTION_DATA = "11223344556677889900aabbccddeeff"
DATA_LENGTH = (Section.LENGTH ** 2) * 2

EXAMPLE_POINT = Point(x=0, y=Section.LENGTH - 1)

FETCH_TEST_CASES = [
    {
        "desc": "fetch all",
        "range": {
            "start_point": EXAMPLE_POINT,
            "end_point": Point(
                x=Section.LENGTH-1,
                y=0
            )
        },
        "expect": EXAPMLE_SECTION_DATA
    },
    {
        "desc": "fetch start",
        "range": {
            "start_point": EXAMPLE_POINT
        },
        "expect": EXAPMLE_SECTION_DATA[0: 2]
    },
    {
        "desc": "fetch end",
        "range": {
            "start_point": Point(
                x=Section.LENGTH - 1,
                y=0
            )
        },
        "expect": EXAPMLE_SECTION_DATA[DATA_LENGTH - 2:]
    }
]


class SectionTestCase(unittest.TestCase):
    def setUp(self):
        self.section = Section.from_str(
            p=EXAMPLE_POINT,
            data=EXAPMLE_SECTION_DATA
        )

    def test_from_str(self):
        self.section = Section.from_str(
            p=EXAMPLE_POINT,
            data=EXAPMLE_SECTION_DATA
        )

        self.assertEqual(self.section.p, EXAMPLE_POINT)

        data_length = len(self.section.data)
        self.assertEqual(data_length, Section.LENGTH ** 2)

    @cases(FETCH_TEST_CASES)
    def test_fetch(self, desc, range, expect):
        start = range["start_point"]
        end = range["end_point"] if "end_point" in range else None

        data = self.section.fetch(start=start, end=end)

        self.assertEqual(data.to_str(), expect, desc)

    def test_fetch_out_of_range(self):
        pass
        # TODO:
        # {
        #     "desc": "fetch out of range",
        #     "range": {
        #         "start_point": Point(
        #             x=EXAMPLE_POINT.x + Section.LENGTH + 1,
        #             y=EXAMPLE_POINT.y
        #             )
        #     },
        #     "expect": IndexError()
        # },

    def test_update_one(self):
        value = Tiles(data=b'A')

        self.section.update(data=value, start=EXAMPLE_POINT)

        got = self.section.fetch(start=EXAMPLE_POINT)
        self.assertEqual(got, value)

    def test_update_range(self):
        rows = 3
        cols = 3

        # 업데이트용 row * col 크기의 2D bytearray 생성
        data = bytearray().join([bytearray.fromhex(f"{i}{i}")*cols for i in range(rows)])
        value = Tiles(data)
        start = EXAMPLE_POINT
        end = Point(2, 1)

        self.section.update(data=value, start=start, end=end)

        got = self.section.fetch(start=start, end=end)
        self.assertEqual(got.data, value.data)

    def test_create(self):
        mine = Tile.create(
            is_open=False,
            is_mine=True,
            is_flag=False,
            color=None,
            number=None,
        )

        sec = Section.create(Point(0, 0))

        total = Section.LENGTH ** 2
        tile_count = int((total * (1 - Section.MINE_RATIO))//1)
        mine_count = total - tile_count

        self.assertEqual(len(sec.data), total)
        self.assertEqual(sec.data.count(mine.data), mine_count)

        num_mask = 0b00000111
        # 숫자 정확한지 확인
        for y in range(Section.LENGTH):
            for x in range(Section.LENGTH):
                idx = (y * Section.LENGTH) + x
                tile = sec.data[idx]
                if tile == mine.data:
                    continue

                got = tile & num_mask
                expected = check_neighbor_mine_count(sec, Point(x, y))

                self.assertEqual(got, expected)


# (x, y)
DELTA = [
    (0, 1), (0, -1), (-1, 0), (1, 0),  # 상하좌우
    (-1, 1), (1, 1), (-1, -1), (1, -1),  # 좌상 우상 좌하 우하
]

MINE_TILE = 0b01000000


def check_neighbor_mine_count(section: Section, pos: Point) -> int:
    result = 0
    # 주변 탐색
    for dx, dy in DELTA:
        nx, ny = pos.x+dx, pos.y+dy
        if \
                nx < 0 or nx >= Section.LENGTH or \
                ny < 0 or ny >= Section.LENGTH:
            continue

        new_idx = (ny * Section.LENGTH) + nx
        nearby_tile = section.data[new_idx]

        if nearby_tile == MINE_TILE:
            result += 1

    return result


if __name__ == "__main__":
    unittest.main()
