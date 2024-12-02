from cursor.data import Cursor, Color
from cursor.data.handler import (
    CursorHandler,
    NoMatchingCursorException,
    AlreadyWatchingException,
    NotWatchableException,
    NotWatchingException
)
from board import Point
import unittest


class CursorHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # /docs/example/cursor-location.png
        CursorHandler.cursor_dict = {
            "A": Cursor(
                conn_id="A",
                position=Point(-3, 3),
                pointer=None,
                new_pointer=None,
                height=6,
                width=6,
                color=Color.BLUE
            ),
            "B": Cursor(
                conn_id="B",
                position=Point(-3, -4),
                pointer=None,
                new_pointer=None,
                height=7,
                width=7,
                color=Color.BLUE
            ),
            "C": Cursor(
                conn_id="C",
                position=Point(2, -1),
                pointer=None,
                new_pointer=None,
                height=4,
                width=4,
                color=Color.BLUE
            )
        }

    def tearDown(self):
        CursorHandler.cursor_dict = {}
        CursorHandler.watchers = {}
        CursorHandler.watching = {}

    def test_create(self):
        conn_id = "example_conn_id"
        _ = CursorHandler.create_cursor(conn_id)

        self.assertIn(conn_id, CursorHandler.cursor_dict)
        self.assertEqual(type(CursorHandler.cursor_dict[conn_id]), Cursor)
        self.assertEqual(CursorHandler.cursor_dict[conn_id].conn_id, conn_id)

    def test_get_cursor(self):
        a_cur: Cursor | None = CursorHandler.get_cursor("A")
        d_cur: Cursor | None = CursorHandler.get_cursor("D")

        self.assertIsNotNone(a_cur)
        self.assertEqual(type(a_cur), Cursor)
        self.assertEqual(a_cur.conn_id, "A")
        self.assertEqual(a_cur.position.x, -3)
        self.assertEqual(a_cur.position.y, 3)
        self.assertIsNone(a_cur.pointer)
        self.assertIsNone(a_cur.new_pointer)
        self.assertEqual(a_cur.height, 6)
        self.assertEqual(a_cur.width, 6)
        self.assertEqual(a_cur.color, Color.BLUE)

        self.assertIsNone(d_cur)

    def test_remove_cursor(self):
        CursorHandler.remove_cursor("A")
        self.assertNotIn("A", CursorHandler.cursor_dict)
        self.assertEqual(len(CursorHandler.cursor_dict), 2)

    def test_exists_range(self):
        result = CursorHandler.exists_range(Point(-3, 3), Point(3, -3))
        result.sort(key=lambda c: c.conn_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].conn_id, "A")
        self.assertEqual(result[1].conn_id, "C")

    def test_view_includes(self):
        result = CursorHandler.view_includes(Point(-3, 0))
        result.sort(key=lambda c: c.conn_id)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].conn_id, "A")
        self.assertEqual(result[1].conn_id, "B")

    def test_add_watcher(self):
        CursorHandler.add_watcher(
            watcher=CursorHandler.cursor_dict["B"],
            watching=CursorHandler.cursor_dict["A"]
        )

        self.assertIn("A", CursorHandler.watchers)
        self.assertIn("B", CursorHandler.watchers["A"])

        self.assertIn("B", CursorHandler.watching)
        self.assertIn("A", CursorHandler.watching["B"])

    def test_add_watcher_not_watchable(self):
        with self.assertRaises(NotWatchableException):
            CursorHandler.add_watcher(
                watcher=CursorHandler.cursor_dict["C"],
                watching=CursorHandler.cursor_dict["A"]
            )

    def test_add_watcher_already_watching(self):
        CursorHandler.add_watcher(
            watcher=CursorHandler.cursor_dict["B"],
            watching=CursorHandler.cursor_dict["A"]
        )

        with self.assertRaises(AlreadyWatchingException):
            CursorHandler.add_watcher(
                watcher=CursorHandler.cursor_dict["B"],
                watching=CursorHandler.cursor_dict["A"]
            )

    def test_add_watcher_no_matching_cursor(self):
        with self.assertRaises(NoMatchingCursorException):
            CursorHandler.add_watcher(
                watcher=Cursor.create("D"),
                watching=CursorHandler.cursor_dict["A"]
            )

    def test_remove_watcher(self):
        CursorHandler.watchers["A"] = ["B"]
        CursorHandler.watching["B"] = ["A", None]

        CursorHandler.remove_watcher(
            watcher=CursorHandler.cursor_dict["B"],
            watching=CursorHandler.cursor_dict["A"]
        )

        self.assertNotIn("A", CursorHandler.watching["B"])
        self.assertNotIn("A", CursorHandler.watchers)

    def test_remove_watcher_not_watching(self):
        with self.assertRaises(NotWatchingException):
            CursorHandler.remove_watcher(
                watcher=CursorHandler.cursor_dict["B"],
                watching=CursorHandler.cursor_dict["A"]
            )

    def test_remove_watcher_no_matching_cursor(self):
        with self.assertRaises(NoMatchingCursorException):
            CursorHandler.remove_watcher(
                watcher=Cursor.create("D"),
                watching=CursorHandler.cursor_dict["A"]
            )

    def test_get_watchers(self):
        CursorHandler.add_watcher(
            watcher=CursorHandler.cursor_dict["B"],
            watching=CursorHandler.cursor_dict["A"]
        )

        a_watchers = CursorHandler.get_watchers("A")
        b_watchers = CursorHandler.get_watchers("B")

        self.assertEqual(len(a_watchers), 1)
        self.assertEqual(a_watchers[0], "B")

        self.assertEqual(len(b_watchers), 0)

    def test_get_watchers_no_matching_cursor(self):
        with self.assertRaises(NoMatchingCursorException):
            CursorHandler.get_watchers("D")

    def test_get_watching(self):
        CursorHandler.add_watcher(
            watcher=CursorHandler.cursor_dict["B"],
            watching=CursorHandler.cursor_dict["A"]
        )

        a_watching = CursorHandler.get_watching("A")
        b_watching = CursorHandler.get_watching("B")

        self.assertEqual(b_watching[0], "A")
        self.assertEqual(len(b_watching), 1)

        self.assertEqual(len(a_watching), 0)

    def test_get_watching_no_matching_cursor(self):
        with self.assertRaises(NoMatchingCursorException):
            CursorHandler.get_watching("D")
