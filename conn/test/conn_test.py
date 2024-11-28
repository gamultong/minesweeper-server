import unittest

from .fixtures import create_connection_mock
from dataclasses import dataclass
from message.payload import Payload
from message import Message
from message.internal.message import DECODABLE_PAYLOAD_DICT
from conn import Conn


@dataclass
class ExamplePayload(Payload):
    event = "example"
    a: int


class ConnectionTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.id = "example"
        self.conn = create_connection_mock()
        self.conn_obj = Conn.create(self.id, self.conn)

        DECODABLE_PAYLOAD_DICT["example"] = ExamplePayload

    def tearDown(self):
        del DECODABLE_PAYLOAD_DICT["example"]
        return super().tearDown()

    def test_create(self):
        self.assertEqual(self.conn_obj.id, self.id)
        self.assertEqual(self.conn_obj.conn, self.conn)

    async def test_accept(self):
        await self.conn_obj.accept()

        self.assertEqual(len(self.conn.accept.mock_calls), 1)

    async def test_close(self):
        await self.conn_obj.close()
        self.assertEqual(len(self.conn.close.mock_calls), 1)

    async def test_send(self):
        msg = Message("example", payload=ExamplePayload(a=0))
        await self.conn_obj.send(msg)

        self.assertEqual(len(self.conn.send_text.mock_calls), 1)
        self.assertEqual(self.conn.send_text.mock_calls[0].args[0], msg.to_str())

    async def test_receive(self):
        msg: Message[ExamplePayload] = Message("example", payload=ExamplePayload(a=0))

        self.conn.receive_text.return_value = msg.to_str()

        got = await self.conn_obj.receive()

        self.assertEqual(len(self.conn.receive_text.mock_calls), 1)
        self.assertEqual(msg.event, got.event)
        self.assertEqual(msg.payload.a, got.payload.a)
