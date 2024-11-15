from models.section_model import Section, Point
from models.map_handler import MapHandler

def cases(case_list):
    def wrapper(func):
        def func_wrapper(*arg, **kwargs):
            for i in case_list:
                kwargs.update(i)
                func(*arg, **kwargs)
        return func_wrapper
    return wrapper


FETCH_CASE = \
[
    { # 가운데
        "data" : {
            "start_p" : Point(-2,1),
            "end_p" : Point(1, -2)
        },
        "expect": "df12df12er56er56"
    },
    { # 전체
        "data" : {
            "start_p" : Point(-4,3),
            "end_p"   : Point(3, -4)
        },
        "expect": "asdf1234asdf1234asdf1234asdf1234qwer5678qwer5678qwer5678qwer5678"
    },
    { # 한개
        "data" : {
            "start_p" : Point(0, 0),
            "end_p"   : Point(0, 0)
        },
        "expect": "1"
    },
]


import unittest
class MapHandlerTestCase(unittest.TestCase):
    @cases(FETCH_CASE)
    def test_fetch(self, data, expect):
        start_p = data["start_p"]
        end_p = data["end_p"]

        data = MapHandler.fetch(start_p, end_p)

        assert data == expect, f"{data} {expect}"     

unittest.main()