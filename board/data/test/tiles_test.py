from board.data import Tiles

import unittest


class TilesTestCase(unittest.TestCase):
    def test_to_str(self):
        data = bytearray().join([bytearray("abc", "ascii") for _ in range(3)])
        tiles = Tiles(data=data)

        s = tiles.to_str()

        self.assertEqual(s, "abcabcabc")
