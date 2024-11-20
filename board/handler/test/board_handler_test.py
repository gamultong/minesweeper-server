import unittest
from unittest.mock import AsyncMock

from board.handler import BoardHandler
from event import EventBroker
from message import Message
from message.payload import FetchTilesPayload, TilesEvent, TilesPayload
from board.test.fixtures import setup_board

class BoardHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        setup_board()

        # 기존 tiles 리시버 비우기
        self.tiles_receivers = []
        if TilesEvent.TILES in EventBroker.event_dict:
            self.tiles_receivers = EventBroker.event_dict[TilesEvent.TILES].copy()
            
        EventBroker.event_dict[TilesEvent.TILES] = []

        # mock으로 대체
        self.mock = AsyncMock()
        self.mock_receiver = EventBroker.add_receiver(TilesEvent.TILES)(func=self.mock)

    def tearDown(self):
        # tiles 리시버 정상화
        EventBroker.remove_receiver(self.mock_receiver)
        EventBroker.event_dict[TilesEvent.TILES] = self.tiles_receivers

    async def test_receive_message(self):
        message = Message(
            event=TilesEvent.FETCH_TILES, 
            payload=FetchTilesPayload(-2,1,1,-2)
        )

        await BoardHandler.receive_fetch_tiles_event(message)

        self.assertEqual(len(self.mock.mock_calls), 1)
        got = self.mock.mock_calls[0].args[0]
        
        assert type(got) == Message
        assert got.event == TilesEvent.TILES
        
        assert type(got.payload) == TilesPayload
        assert got.payload.start_x == -2
        assert got.payload.start_y == 1
        assert got.payload.end_x == 1
        assert got.payload.end_y == -2
        assert got.payload.tiles == "df12df12er56er56"

if __name__ == "__main__":
    unittest.main()