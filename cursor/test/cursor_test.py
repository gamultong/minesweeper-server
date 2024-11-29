from cursor import Cursor, Color
from board import Point
import unittest


class CursorTestCase(unittest.TestCase):
    def test_cursor_create(self):
        conn_id = "some id"
        cursor = Cursor.create(conn_id)

        self.assertEqual(cursor.conn_id, conn_id)
        self.assertEqual(cursor.position.x, 0)
        self.assertEqual(cursor.position.y, 0)
        self.assertIsNone(cursor.pointer)
        self.assertIn(cursor.color, Color)
        self.assertEqual(cursor.width, 0)
        self.assertEqual(cursor.height, 0)

    def test_check_interactable(self):
        cursor = Cursor.create("")
        cursor.position = Point(0, 0)

        # 자기 자리
        self.assertTrue(cursor.check_interactable(Point(0, 0)))
        # 상하좌우
        self.assertTrue(cursor.check_interactable(Point(0, 1)))
        self.assertTrue(cursor.check_interactable(Point(0, -1)))
        self.assertTrue(cursor.check_interactable(Point(-1, 0)))
        self.assertTrue(cursor.check_interactable(Point(1, 0)))
        # 좌상 우상 좌하 우하
        self.assertTrue(cursor.check_interactable(Point(-1, 1)))
        self.assertTrue(cursor.check_interactable(Point(1, 1)))
        self.assertTrue(cursor.check_interactable(Point(-1, -1)))
        self.assertTrue(cursor.check_interactable(Point(1, -1)))

        # 벗어남
        self.assertFalse(cursor.check_interactable(Point(1, 2)))
        self.assertFalse(cursor.check_interactable(Point(5, 1)))
        self.assertFalse(cursor.check_interactable(Point(0, -3)))


if __name__ == "__main__":
    unittest.main()
