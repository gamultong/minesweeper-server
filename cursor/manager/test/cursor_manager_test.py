from cursor import Cursor, Color
from cursor.manager import CursorManager
from event import EventBroker
from message import Message
from message.payload import NewConnEvent, NewConnPayload
import unittest
from unittest.mock import Mock, AsyncMock
from board import Point
from warnings import warn


def get_cur(conn_id):
    return Cursor(
        conn_id=conn_id,
        position=Point(0, 0),
        pointer=None,
        height=10,
        width=10,
        color=Color.BLUE
    )


class CursorManagerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        CursorManager.cursor_dict = {
            "example_1": get_cur("example_1"),
            "example_2": get_cur("example_2"),
            "example_3": get_cur("example_3")
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

        self.assertEqual(len(result), 3)

    def test_view_includes(self):
        result = CursorManager.view_includes(Point(0, 0))

        self.assertEqual(len(result), 3)


class CursorManagerNewConnTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # 기존 my-cursor 리시버 비우기 및 mock으로 대체
        self.multicast_receivers = []
        if "multicast" in EventBroker.event_dict:
            self.multicast_receivers = EventBroker.event_dict["multicast"].copy()

        EventBroker.event_dict["multicast"] = []

        self.mock_multicast_func = AsyncMock()
        self.mock_multicast_receiver = EventBroker.add_receiver(event="multicast")(func=self.mock_multicast_func)

    def tearDown(self):
        # 리시버 정상화
        EventBroker.remove_receiver(self.mock_multicast_receiver)
        EventBroker.event_dict["multicast"] = self.multicast_receivers

        CursorManager.cursor_dict = {}

    async def test_receive_new_conn_without_cursors(self):
        CursorManager.cursor_dict = {}

        expected_conn_id = "example"
        expected_height = 100
        expected_width = 100

        message = Message(
            event=NewConnEvent.NEW_CONN,
            payload=NewConnPayload(
                conn_id=expected_conn_id,
                width=expected_width,
                height=expected_height
            )
        )

        await CursorManager.receive_new_conn(message)

        self.assertEqual(len(self.mock_multicast_func.mock_calls), 3)
        got = self.mock_multicast_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == "multicast"

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == 1
        assert got.header["target_conns"][0] == expected_conn_id

    async def test_receive_new_conn_with_cursors(self):

        # TODO: 쿼리 로직 바뀌면 이것도 같이 바꿔야 함.
        CursorManager.cursor_dict = {
            "some id": Cursor.create("some id")
        }

        expected_conn_id = "example"
        expected_height = 100
        expected_width = 100

        message = Message(
            event=NewConnEvent.NEW_CONN,
            payload=NewConnPayload(
                conn_id=expected_conn_id,
                width=expected_width,
                height=expected_height
            )
        )

        await CursorManager.receive_new_conn(message)

        self.assertEqual(len(self.mock_multicast_func.mock_calls), 3)
        got = self.mock_multicast_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == "multicast"

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == 1
        assert got.header["target_conns"][0] == expected_conn_id

        got = self.mock_multicast_func.mock_calls[1].args[0]

        assert type(got) == Message
        assert got.event == "multicast"

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == 1
        assert got.header["target_conns"][0] == expected_conn_id

        got = self.mock_multicast_func.mock_calls[2].args[0]

        assert type(got) == Message
        assert got.event == "multicast"

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == len(CursorManager.cursor_dict)
        assert set(got.header["target_conns"]) == set([c.conn_id for c in CursorManager.cursor_dict.values()])


if __name__ == "__main__":
    unittest.main()
