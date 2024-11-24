from cursor import Cursor
from cursor.manager import CursorManager
import unittest
from unittest.mock import Mock
from board import Point
from warnings import warn


class CursorManagerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.curs_1 = Mock()
        self.curs_2 = Mock()
        self.curs_3 = Mock()
        CursorManager.cursor_dict = {
            "example_1": self.curs_1,
            "example_2": self.curs_2,
            "example_3": self.curs_3
        }

    def tearDown(self):
        CursorManager.cursor_dict = {}

    def test_create(self):
        conn_id = "example_conn_id"
        CursorManager.create(conn_id)

        self.assertIn(conn_id, CursorManager.cursor_dict)
        self.assertEqual(type(CursorManager.cursor_dict[conn_id]), Cursor)
        self.assertEqual(CursorManager.cursor_dict[conn_id].conn_id, conn_id)

    def test_remove(self):
        CursorManager.remove("example_1")
        self.assertNotIn("example_1", CursorManager.cursor_dict)
        self.assertEqual(len(CursorManager.cursor_dict), 2)

    def test_exists_range(self):
        result = CursorManager.exists_range(Point(0, 0), Point(0, 0))

        warn("아직 구현 안됨")
        # broadcast 기준
        self.assertEqual(len(result), 3)

    def test_view_includes(self):
        result = CursorManager.view_includes(Point(0, 0))

        warn("아직 구현 안됨")
        # broadcast 기준
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
