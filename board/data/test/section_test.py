import unittest
from tests.utils import cases
from board.data import Section, Point


# 테스트를 위해 Section.LENGTH를 4로 설정
Section.LENGTH = 4

EXAPMLE_SECTION_DATA = "asdfasdfadsfasdf"

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
        "expect": EXAPMLE_SECTION_DATA[0]
    },
    {
        "desc": "fetch end",
        "range": {
            "start_point": Point(
                x=Section.LENGTH - 1,
                y=0
            )
        },
        "expect": EXAPMLE_SECTION_DATA[(Section.LENGTH ** 2) - 1]
    }
]


class SectionTestCase(unittest.TestCase):
    def setUp(self):
        self.section = Section.from_str(
            p=EXAMPLE_POINT,
            data=EXAPMLE_SECTION_DATA
        )

    def test_create(self):
        self.section = Section.from_str(
            p=EXAMPLE_POINT,
            data=EXAPMLE_SECTION_DATA
        )

        self.assertEqual(self.section.p, EXAMPLE_POINT)

        data_length = sum(len(row) for row in self.section.data)
        self.assertEqual(data_length, Section.LENGTH ** 2)

    @cases(FETCH_TEST_CASES)
    def test_fetch(self, desc, range, expect):
        start = range["start_point"]
        end = range["end_point"] if "end_point" in range else None

        data = self.section.fetch(start=start, end=end)

        # list[bytearray]인 경우 1차원으로 flatten
        if end is not None:
            data = bytearray().join(data)

        self.assertEqual(data.decode('ascii'), expect, desc)

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
        value = b'A'

        self.section.update(data=value, start=EXAMPLE_POINT)

        got = self.section.fetch(start=EXAMPLE_POINT)
        self.assertEqual(got, value)

    def test_update_range(self):
        rows = 3
        cols = 3

        # 업데이트용 row * col 크기의 2D bytearray 생성
        value = [bytearray(f"{i}"*cols, "ascii") for i in range(rows)]
        start = EXAMPLE_POINT
        end = Point(2, 1)

        self.section.update(data=value, start=start, end=end)

        got = self.section.fetch(start=start, end=end)
        self.assertEqual(got, value)


if __name__ == "__main__":
    unittest.main()
