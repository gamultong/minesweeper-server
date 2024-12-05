from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

from server import app
from message import Message
from message.payload import FetchTilesPayload, TilesPayload, TilesEvent, NewConnEvent
from board.data.handler.test.fixtures import setup_board
from board.event.handler import BoardEventHandler
from board.data import Point, Tile, Tiles
from event import EventBroker
from conn.manager import ConnectionManager

import unittest
from unittest.mock import AsyncMock, patch


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        setup_board()
        self.client = TestClient(app)

        self.client.headers["X-View-Tiles-Width"] = "1"
        self.client.headers["X-View-Tiles-Height"] = "1"

    def tearDown(self):
        self.client.headers = {}
        self.client.close()

    def test_no_headers(self):
        self.client.headers = {}

        with self.assertRaises(WebSocketDisconnect) as cm:
            with self.client.websocket_connect("/session") as websocket:
                websocket.close()

    def test_wrong_headers(self):
        self.client.headers["X-View-Tiles-Width"] = "string"

        with self.assertRaises(WebSocketDisconnect) as cm:
            with self.client.websocket_connect("/session") as websocket:
                websocket.close()

    @patch("event.EventBroker.publish")
    def test_fetch_tiles(self, mock: AsyncMock):
        async def filter_tiles_event(message: Message):
            match (message.event):
                case "multicast":
                    await ConnectionManager.receive_multicast_event(message)
                case TilesEvent.FETCH_TILES:
                    await BoardEventHandler.receive_fetch_tiles(message)

        mock.side_effect = filter_tiles_event

        with self.client.websocket_connect("/session") as websocket:
            msg = Message(
                event=TilesEvent.FETCH_TILES,
                payload=FetchTilesPayload(
                    start_p=Point(-2, 1),
                    end_p=Point(1, -2)
                )
            )

            empty_open = Tile.from_int(0b10000000)
            one_open = Tile.from_int(0b10000001)
            expected = Tiles(data=bytearray([
                empty_open.data, one_open.data, one_open.data, one_open.data
            ]))

            expect = Message(
                event=TilesEvent.TILES,
                payload=TilesPayload(
                    start_p=Point(-2, 1),
                    end_p=Point(1, -2),
                    tiles=expected.to_str()
                )
            )

            websocket.send_text(msg.to_str())

            # TODO: 이거 고치기
            # response = websocket.receive_text()
            # self.assertEqual(response, expect.to_str())


if __name__ == "__main__":
    unittest.main()
