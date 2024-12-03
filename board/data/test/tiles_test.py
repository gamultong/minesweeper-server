from board.data import Tiles

import unittest


class TilesTestCase(unittest.TestCase):
    def test_to_str(self):
        tiles = Tiles(data=[bytearray("abc", "ascii") for _ in range(3)])

        s = tiles.to_str()

        self.assertEqual(s, "abcabcabc")
