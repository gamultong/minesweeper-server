from cursor import Cursor
from cursor.manager import CursorManager
from event import EventBroker
from message import Message
from message.payload import NewConnEvent, NewConnPayload
import unittest
from unittest.mock import Mock, AsyncMock
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


class CursorManagerNewConnTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # 기존 my-cursor 리시버 비우기 및 mock으로 대체
        self.my_cursor_receivers = []
        if NewConnEvent.MY_CURSOR in EventBroker.event_dict:
            self.my_cursor_receivers = EventBroker.event_dict[NewConnEvent.MY_CURSOR].copy()

        EventBroker.event_dict[NewConnEvent.MY_CURSOR] = []

        self.mock_my_cursor_func = AsyncMock()
        self.mock_my_cursor_receiver = EventBroker.add_receiver(event=NewConnEvent.MY_CURSOR)(func=self.mock_my_cursor_func)

        # 기존 nearby-cursor 리시버 비우기 및 mock으로 대체
        self.nearby_cursor_receivers = []
        if NewConnEvent.NEARYBY_CURSORS in EventBroker.event_dict:
            self.nearby_cursor_receivers = EventBroker.event_dict[NewConnEvent.NEARYBY_CURSORS].copy()

        EventBroker.event_dict[NewConnEvent.NEARYBY_CURSORS] = []

        self.mock_nearby_cursor_func = AsyncMock()
        self.mock_nearby_cursor_receiver = EventBroker.add_receiver(event=NewConnEvent.NEARYBY_CURSORS)(func=self.mock_nearby_cursor_func)

        # 기존 cursor-appeared 리시버 비우기 및 mock으로 대체
        self.cursor_appeared_receivers = []
        if NewConnEvent.CURSOR_APPEARED in EventBroker.event_dict:
            self.cursor_appeared_receivers = EventBroker.event_dict[NewConnEvent.CURSOR_APPEARED].copy()

        EventBroker.event_dict[NewConnEvent.CURSOR_APPEARED] = []

        self.mock_cursor_appeared_func = AsyncMock()
        self.mock_cursor_appeared_receiver = EventBroker.add_receiver(event=NewConnEvent.CURSOR_APPEARED)(func=self.mock_cursor_appeared_func)

    def tearDown(self):
        # 리시버 정상화
        EventBroker.remove_receiver(self.mock_my_cursor_receiver)
        EventBroker.event_dict[NewConnEvent.MY_CURSOR] = self.my_cursor_receivers
        EventBroker.remove_receiver(self.mock_nearby_cursor_receiver)
        EventBroker.event_dict[NewConnEvent.NEARYBY_CURSORS] = self.nearby_cursor_receivers
        EventBroker.remove_receiver(self.mock_cursor_appeared_receiver)
        EventBroker.event_dict[NewConnEvent.CURSOR_APPEARED] = self.cursor_appeared_receivers

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

        self.assertEqual(len(self.mock_my_cursor_func.mock_calls), 1)
        got = self.mock_my_cursor_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == NewConnEvent.MY_CURSOR

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

        self.assertEqual(len(self.mock_my_cursor_func.mock_calls), 1)
        got = self.mock_my_cursor_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == NewConnEvent.MY_CURSOR

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == 1
        assert got.header["target_conns"][0] == expected_conn_id

        self.assertEqual(len(self.mock_nearby_cursor_func.mock_calls), 1)
        got = self.mock_nearby_cursor_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == NewConnEvent.NEARYBY_CURSORS

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == 1
        assert got.header["target_conns"][0] == expected_conn_id

        self.assertEqual(len(self.mock_cursor_appeared_func.mock_calls), 1)
        got = self.mock_cursor_appeared_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == NewConnEvent.CURSOR_APPEARED

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == len(CursorManager.cursor_dict)
        assert set(got.header["target_conns"]) == set([c.conn_id for c in CursorManager.cursor_dict.values()])


if __name__ == "__main__":
    unittest.main()
