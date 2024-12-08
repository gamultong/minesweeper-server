import unittest
from tests.utils import cases
from board.data import Point, Tile
from board.data.handler import BoardHandler
from .fixtures import setup_board

FETCH_CASE = \
    [
        {  # 가운데
            "data": {
                "start_p": Point(-2, 1),
                "end_p": Point(1, -2)
            },
            "expect": "82818170818081018281813983680302"
        },
        {  # 전체
            "data": {
                "start_p": Point(-4, 3),
                "end_p": Point(3, -4)
            },
            "expect": "0102020100000000014040010101010001028281817001000121818081010100014082818139010181818368030240018080824003400201c080810102010100"
        },
        {  # 한개
            "data": {
                "start_p": Point(0, 0),
                "end_p": Point(0, 0)
            },
            "expect": "81"
        }
    ]


class BoardHandlerTestCase(unittest.TestCase):
    def setUp(self):
        setup_board()

    @cases(FETCH_CASE)
    def test_fetch(self, data, expect):
        start_p = data["start_p"]
        end_p = data["end_p"]

        tiles = BoardHandler.fetch(start_p, end_p)
        data = tiles.to_str()

        self.assertEqual(data,  expect)

    def test_fetch_out_of_bounds(self):
        # 오른쪽 섹션 추가
        start = Point(4, 3)
        end = Point(6, 1)

        BoardHandler.fetch(start, end)

        sx, sy = 1, 0
        self.assertIsNotNone(BoardHandler.sections[sy][sx])

    def test_update_tile(self):
        p = Point(-1, -1)

        tile = Tile.from_int(0)
        BoardHandler.update_tile(p=p, tile=tile)

        tiles = BoardHandler.fetch(start=p, end=p)

        self.assertEqual(tiles.data[0], tile.data)


if __name__ == "__main__":
    unittest.main()
