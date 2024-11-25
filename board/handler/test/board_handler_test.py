import unittest
from unittest.mock import AsyncMock

from board.handler import BoardHandler
from event import EventBroker
from message import Message
from message.payload import FetchTilesPayload, TilesEvent, TilesPayload, NewConnEvent, NewConnPayload
from board.test.fixtures import setup_board


class BoardHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        setup_board()

        # 기존 tiles 리시버 비우기 및 mock으로 대체
        self.tiles_receivers = []
        if TilesEvent.TILES in EventBroker.event_dict:
            self.tiles_receivers = EventBroker.event_dict[TilesEvent.TILES].copy()

        EventBroker.event_dict[TilesEvent.TILES] = []

        self.mock_fetch_tiles_func = AsyncMock()
        self.mock_fetch_tiles_receiver = EventBroker.add_receiver(TilesEvent.TILES)(func=self.mock_fetch_tiles_func)

    def tearDown(self):
        # 리시버 정상화
        EventBroker.remove_receiver(self.mock_fetch_tiles_receiver)
        EventBroker.event_dict[TilesEvent.TILES] = self.tiles_receivers

    async def test_receive_fetch_tiles(self):
        message = Message(
            event=TilesEvent.FETCH_TILES,
            payload=FetchTilesPayload(-2, 1, 1, -2)
        )

        await BoardHandler.receive_fetch_tiles(message)

        self.assertEqual(len(self.mock_fetch_tiles_func.mock_calls), 1)
        got = self.mock_fetch_tiles_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == TilesEvent.TILES

        assert type(got.payload) == TilesPayload
        assert got.payload.start_x == -2
        assert got.payload.start_y == 1
        assert got.payload.end_x == 1
        assert got.payload.end_y == -2
        assert got.payload.tiles == "df12df12er56er56"

    async def test_receive_new_conn(self):
        message = Message(
            event=NewConnEvent.NEW_CONN,
            payload=NewConnPayload(conn_id="not important", width=2, height=2)
        )

        await BoardHandler.receive_new_conn(message)

        self.assertEqual(len(self.mock_fetch_tiles_func.mock_calls), 1)
        got = self.mock_fetch_tiles_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == TilesEvent.TILES

        assert type(got.payload) == TilesPayload
        assert got.payload.start_x == -2
        assert got.payload.start_y == 2
        assert got.payload.end_x == 2
        assert got.payload.end_y == -2
        assert got.payload.tiles == "df123df123df123er567er567"


if __name__ == "__main__":
    unittest.main()
