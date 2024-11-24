from message import Message, InvalidEventTypeException
from message.payload import Payload, FetchTilesPayload, TilesPayload
from .message_testdata import FETCH_TILES_EXAMPLE, INVALID_EVENT_EXAMPLE, TILES_EXAMPLE

import unittest
import json


class MessageTestCase(unittest.TestCase):
    def test_fetch_tiles_from_str(self):
        socket_msg = FETCH_TILES_EXAMPLE
        message: Message[FetchTilesPayload] = Message.from_str(socket_msg)

        assert message.event == "fetch-tiles"
        assert issubclass(type(message.payload), Payload)
        assert message.payload.start_x == 0
        assert message.payload.start_y == 0
        assert message.payload.end_x == 0
        assert message.payload.end_y == 0

    def test_fetch_tiles_to_str(self):
        message: Message[FetchTilesPayload] = Message(
            event="fetch-tiles",
            payload=FetchTilesPayload(
                start_x=0,
                start_y=0,
                end_x=0,
                end_y=0,
            )
        )

        msg_str = message.to_str()

        assert json.loads(msg_str) == json.loads(FETCH_TILES_EXAMPLE)

    def test_tiles_from_str(self):
        socket_msg = TILES_EXAMPLE
        message: Message[TilesPayload] = Message.from_str(socket_msg)

        assert message.event == "tiles"
        assert issubclass(type(message.payload), Payload)
        assert message.payload.start_x == 0
        assert message.payload.start_y == 0
        assert message.payload.end_x == 4
        assert message.payload.end_y == 4
        assert message.payload.tiles == "CCCCCCCCCCC111CC1F1CC111C"

    def test_tiles_to_str(self):
        message: Message[TilesPayload] = Message(
            event="tiles",
            payload=TilesPayload(
                start_x=0,
                start_y=0,
                end_x=4,
                end_y=4,
                tiles="CCCCCCCCCCC111CC1F1CC111C"
            )
        )

        msg_str = message.to_str()

        assert json.loads(msg_str) == json.loads(TILES_EXAMPLE)

    def test_from_str_invalid_event(self):
        socket_msg = INVALID_EVENT_EXAMPLE

        with self.assertRaises(InvalidEventTypeException) as cm:
            Message.from_str(socket_msg)

        assert cm.exception.msg == "invalid event type: 'ayo invalid'", cm.exception.msg


if __name__ == "__main__":
    unittest.main()
