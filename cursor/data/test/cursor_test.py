from cursor.data import Cursor, Color
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


if __name__ == "__main__":
    unittest.main()
