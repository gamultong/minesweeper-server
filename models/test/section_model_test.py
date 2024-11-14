from models.section_model import *

import unittest

TESTDATA_PATH = "testdata/map_example.txt"
EXAPMLE_SECTION_DATA = open(TESTDATA_PATH, "r").readline()

EXAMPLE_POINT = Point(x=0, y=0)

def cases(case_list):
    def wrapper(func):
        def func_wrapper(*arg, **kwargs):
            for i in case_list:
                kwargs.update(i)
                func(*arg, **kwargs)
        return func_wrapper
    return wrapper


testcases = [
    {
        "desc": "fetch all",
        "range": {
            "start_point": EXAMPLE_POINT,
            "end_point": Point(
                x=EXAMPLE_POINT.x + SECTION_LENGTH-1, 
                y=EXAMPLE_POINT.y + SECTION_LENGTH-1
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
                x=EXAMPLE_POINT.x + SECTION_LENGTH - 1, 
                y=EXAMPLE_POINT.y + SECTION_LENGTH - 1
                )
        },
        "expect": EXAPMLE_SECTION_DATA[(SECTION_LENGTH ** 2) - 1]
    },
    # ToDo
    # {
    #     "desc": "fetch out of range",
    #     "range": {
    #         "start_point": Point(
    #             x=EXAMPLE_POINT.x + SECTION_LENGTH + 1, 
    #             y=EXAMPLE_POINT.y
    #             )
    #     },
    #     "expect": IndexError()
    # },
]

class SectionModelTestCase(unittest.TestCase):
    def test_create(self):
        section = Section.from_str(
            p=EXAMPLE_POINT, 
            data=EXAPMLE_SECTION_DATA
            )
        
        assert section.p == EXAMPLE_POINT

        data_length = sum(len(row) for row in section.data)
        assert data_length == SECTION_LENGTH ** 2, data_length

        assert bytearray().join(section[:][:]) == bytearray(EXAPMLE_SECTION_DATA, 'ascii')

    @cases(testcases)
    def test_fetch(self, desc, range, expect):
        section = Section.from_str(
            p=EXAMPLE_POINT,
            data=EXAPMLE_SECTION_DATA
            )

        start = range["start_point"]
        end = range["end_point"] if "end_point" in range else None

        if isinstance(expect, BaseException):
            with self.assertRaises(expect, msg=f"desc: {desc}"):
                section.fetch(start=start, end=end)
        else:
                
            data = section.fetch(start=start, end=end)

            if not end:
                data = [data]

            data = bytearray().join(data)
            
            expect = bytearray(expect, "ascii")
            assert data == expect, f"desc: {desc}, {data}, {expect}"

    def test_update_one(self):
        section = Section.from_str(
            p=EXAMPLE_POINT,
            data=EXAPMLE_SECTION_DATA
            )

        value = b'A'
        section.update(data=value, start=EXAMPLE_POINT)

        got = section.fetch(start=EXAMPLE_POINT)
        assert got == value, f"{type(got)} {got} {value}"

    def test_update_range(self):
        section = Section.from_str(
            p=EXAMPLE_POINT,
            data=EXAPMLE_SECTION_DATA
            )

        rows = 3
        cols = 3

        value = [bytearray("A"*cols, "ascii") for _ in range(rows)]
        start = EXAMPLE_POINT
        end = Point(EXAMPLE_POINT.x + cols - 1, EXAMPLE_POINT.y + rows - 1)

        section.update(data=value, start=start, end=end)

        got = section.fetch(start=start, end=end)
        assert got == value, f"{got} {value}"



unittest.main()