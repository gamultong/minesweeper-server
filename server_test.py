from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from server import app
from message import Message
from message.payload import FetchTilesPayload, TilesPayload, TilesEvent, NewConnEvent
from board.test.fixtures import setup_board
from event import EventBroker
from board import Point
import unittest
from unittest.mock import AsyncMock


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

    def test_fetch_tiles(self):
        # 기존 new-conn 리시버 비우기 및 mock으로 대체
        self.new_conn_receivers = []
        if NewConnEvent.NEW_CONN in EventBroker.event_dict:
            self.new_conn_receivers = EventBroker.event_dict[NewConnEvent.NEW_CONN].copy()

        EventBroker.event_dict[NewConnEvent.NEW_CONN] = []

        self.mock_new_conn_func = AsyncMock()
        self.mock_new_conn_receiver = EventBroker.add_receiver(NewConnEvent.NEW_CONN)(func=self.mock_new_conn_func)

        with self.client.websocket_connect("/session") as websocket:
            msg = Message(
                event=TilesEvent.FETCH_TILES,
                payload=FetchTilesPayload(
                    start_p=Point(-2, 1),
                    end_p=Point(1, -2)
                )
            )

            expect = Message(
                event=TilesEvent.TILES,
                payload=TilesPayload(
                    start_p=Point(-2, 1),
                    end_p=Point(1, -2),
                    tiles="df12df12er56er56"
                )
            )

            websocket.send_text(msg.to_str())

            response = websocket.receive_text()

            assert response == expect.to_str()

        # 리시버 정상화
        EventBroker.remove_receiver(self.mock_new_conn_receiver)
        EventBroker.event_dict[NewConnEvent.NEW_CONN] = self.new_conn_receivers


if __name__ == "__main__":
    unittest.main()
