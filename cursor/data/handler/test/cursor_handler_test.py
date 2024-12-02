from cursor.data import Cursor, Color
from cursor.data.handler import CursorHandler
from board import Point
import unittest


def get_cur(conn_id):
    return Cursor(
        conn_id=conn_id,
        position=Point(0, 0),
        pointer=None,
        new_pointer=None,
        height=10,
        width=10,
        color=Color.BLUE
    )


class CursorHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        CursorHandler.cursor_dict = {
            "example_1": get_cur("example_1"),
            "example_2": get_cur("example_2"),
            "example_3": get_cur("example_3")
        }

    def tearDown(self):
        CursorHandler.cursor_dict = {}

    def test_create(self):
        conn_id = "example_conn_id"
        CursorHandler.create(conn_id)

        self.assertIn(conn_id, CursorHandler.cursor_dict)
        self.assertEqual(type(CursorHandler.cursor_dict[conn_id]), Cursor)
        self.assertEqual(CursorHandler.cursor_dict[conn_id].conn_id, conn_id)

    def test_remove(self):
        CursorHandler.remove("example_1")
        self.assertNotIn("example_1", CursorHandler.cursor_dict)
        self.assertEqual(len(CursorHandler.cursor_dict), 2)

    def test_exists_range(self):
        result = CursorHandler.exists_range(Point(0, 0), Point(0, 0))

        self.assertEqual(len(result), 3)

    def test_view_includes(self):
        result = CursorHandler.view_includes(Point(0, 0))

        self.assertEqual(len(result), 3)
