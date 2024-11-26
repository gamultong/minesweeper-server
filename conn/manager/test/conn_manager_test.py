import unittest
import uuid

from unittest.mock import MagicMock, AsyncMock
from conn import Conn
from conn.manager import ConnectionManager
from message import Message
from message.payload import TilesPayload, NewConnEvent, NewConnPayload
from event import EventBroker
from conn.test.fixtures import create_connection_mock


class ConnectionManagerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.con1 = create_connection_mock()
        self.con2 = create_connection_mock()
        self.con3 = create_connection_mock()
        self.con4 = create_connection_mock()

        # 기존 new-conn 리시버 비우기 및 mock으로 대체
        self.new_conn_receivers = []
        if NewConnEvent.NEW_CONN in EventBroker.event_dict:
            self.new_conn_receivers = EventBroker.event_dict[NewConnEvent.NEW_CONN].copy()

        EventBroker.event_dict[NewConnEvent.NEW_CONN] = []

        self.mock_new_conn_func = AsyncMock()
        self.mock_new_conn_receiver = EventBroker.add_receiver(NewConnEvent.NEW_CONN)(func=self.mock_new_conn_func)

    def tearDown(self):
        ConnectionManager.conns = {}

        # 리시버 정상화
        EventBroker.remove_receiver(self.mock_new_conn_receiver)
        EventBroker.event_dict[NewConnEvent.NEW_CONN] = self.new_conn_receivers

    async def test_add(self):

        width = 1
        height = 1

        con_obj = await ConnectionManager.add(self.con1, width, height)
        assert type(con_obj) == Conn

        assert ConnectionManager.get_conn(con_obj.id).id == con_obj.id

        assert len(self.mock_new_conn_func.mock_calls) == 1

        got = self.mock_new_conn_func.mock_calls[0].args[0]
        assert type(got) == Message
        assert type(got.payload) == NewConnPayload
        assert got.payload.conn_id == con_obj.id
        assert got.payload.width == width
        assert got.payload.height == height

    def test_get_conn(self):
        valid_id = "abc"
        invalid_id = "abcdef"
        ConnectionManager.conns[valid_id] = Conn(valid_id, create_connection_mock())

        assert ConnectionManager.get_conn(valid_id) is not None
        assert ConnectionManager.get_conn(invalid_id) is None

    async def test_generate_conn_id(self):
        n_conns = 5

        conns = [create_connection_mock() for _ in range(n_conns)]
        conn_ids = [None] * n_conns

        for idx, conn in enumerate(conns):
            conn_obj = await ConnectionManager.add(conn=conn, width=1, height=1)
            conn_ids[idx] = conn_obj.id

        for id in conn_ids:
            assert conn_ids.count(id) == 1
            # UUID 포맷인지 확인. 아니면 ValueError
            uuid.UUID(id)

    async def test_receive_broadcast_event(self):
        _ = await ConnectionManager.add(self.con1, 1, 1)
        _ = await ConnectionManager.add(self.con2, 1, 1)
        _ = await ConnectionManager.add(self.con3, 1, 1)
        _ = await ConnectionManager.add(self.con4, 1, 1)

        origin_event = "ayo"

        message = Message(event="broadcast", header={"origin_event": origin_event}, payload=None)

        await EventBroker.publish(message)

        expected = Message(event=origin_event, payload=None)

        self.assertEqual(len(self.con1.send_text.mock_calls), 1)
        self.assertEqual(len(self.con2.send_text.mock_calls), 1)
        self.assertEqual(len(self.con3.send_text.mock_calls), 1)
        self.assertEqual(len(self.con4.send_text.mock_calls), 1)

        self.assertEqual(expected.to_str(), self.con1.send_text.mock_calls[0].args[0])
        self.assertEqual(expected.to_str(), self.con2.send_text.mock_calls[0].args[0])
        self.assertEqual(expected.to_str(), self.con3.send_text.mock_calls[0].args[0])
        self.assertEqual(expected.to_str(), self.con4.send_text.mock_calls[0].args[0])

    async def test_receive_multicast_event(self):
        con1 = await ConnectionManager.add(self.con1, 1, 1)
        con2 = await ConnectionManager.add(self.con2, 1, 1)
        _ = await ConnectionManager.add(self.con3, 1, 1)
        _ = await ConnectionManager.add(self.con4, 1, 1)

        origin_event = "ayo"

        message = Message(
            event="multicast",
            header={
                "target_conns": [con1.id, con2.id],
                "origin_event": origin_event
            },
            payload=None
        )

        expected = Message(event=origin_event, payload=None)

        await EventBroker.publish(message)

        self.assertEqual(len(self.con1.send_text.mock_calls), 1)
        self.assertEqual(len(self.con2.send_text.mock_calls), 1)
        self.assertEqual(len(self.con3.send_text.mock_calls), 0)
        self.assertEqual(len(self.con4.send_text.mock_calls), 0)

        self.assertEqual(expected.to_str(), self.con1.send_text.mock_calls[0].args[0])
        self.assertEqual(expected.to_str(), self.con2.send_text.mock_calls[0].args[0])

    async def test_handle_message(self):
        mock = AsyncMock()
        EventBroker.add_receiver("example")(mock)

        conn_id = "haha this is some random conn id"
        message = Message(event="example",
                          header={"sender": conn_id},
                          payload=TilesPayload(
                              0, 0, 0, 0, "abcdefg"
                          ))

        await ConnectionManager.handle_message(message=message)

        self.assertEqual(len(mock.mock_calls), 1)

        got = mock.mock_calls[0].args[0]
        self.assertEqual(got.header["sender"], conn_id)
        self.assertEqual(got.to_str(), message.to_str())


if __name__ == "__main__":
    unittest.main()
