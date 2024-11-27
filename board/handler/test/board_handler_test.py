import unittest
from unittest.mock import AsyncMock

from board.handler import BoardHandler
from event import EventBroker
from message import Message
from message.payload import FetchTilesPayload, TilesEvent, TilesPayload, NewConnEvent, NewConnPayload, TryPointingPayload, PointingResultPayload, PointEvent

from board.test.fixtures import setup_board
from board import Point

from cursor import Color
from event.internal.event_broker import Receiver


class BoardHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        setup_board()

        # 기존 tiles 리시버 비우기 및 mock으로 대체
        self.multi_receivers = []
        if "multicast" in EventBroker.event_dict:
            self.multi_receivers = EventBroker.event_dict["multicast"].copy()

        EventBroker.event_dict["multicast"] = []

        self.mock_multicast_func = AsyncMock()
        self.mock_multicast_receiver = EventBroker.add_receiver("multicast")(func=self.mock_multicast_func)

        self.pointing_result_receivers = []
        if PointEvent.POINTING_RESULT in EventBroker.event_dict:
            self.pointing_result_receivers = EventBroker.event_dict[PointEvent.POINTING_RESULT].copy()

        EventBroker.event_dict[PointEvent.POINTING_RESULT] = []

        self.mock_pointing_result_func = AsyncMock()
        self.mock_pointing_result_receiver = EventBroker.add_receiver(PointEvent.POINTING_RESULT)(func=self.mock_pointing_result_func)

    def tearDown(self):
        # 리시버 정상화
        EventBroker.remove_receiver(self.mock_multicast_receiver)
        EventBroker.event_dict["multicast"] = self.multi_receivers

        EventBroker.remove_receiver(self.mock_pointing_result_receiver)
        EventBroker.event_dict[PointEvent.POINTING_RESULT] = self.pointing_result_receivers

    async def test_receive_fetch_tiles(self):
        message = Message(
            event=TilesEvent.FETCH_TILES,
            payload=FetchTilesPayload(Point(-2, 1), Point(1, -2)),
            header={"sender": "ayo"},

        )

        await BoardHandler.receive_fetch_tiles(message)

        self.assertEqual(len(self.mock_multicast_func.mock_calls), 1)
        got = self.mock_multicast_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == "multicast"

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == 1
        assert got.header["target_conns"][0] == message.header["sender"]

        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], TilesEvent.TILES)

        assert type(got.payload) == TilesPayload
        assert got.payload.start_p.x == -2
        assert got.payload.start_p.y == 1
        assert got.payload.end_p.x == 1
        assert got.payload.end_p.y == -2
        assert got.payload.tiles == "df12df12er56er56"

    async def test_receive_new_conn(self):
        message = Message(
            event=NewConnEvent.NEW_CONN,
            header={"sender": "ayo"},
            payload=NewConnPayload(conn_id="not important", width=2, height=2)
        )

        await BoardHandler.receive_new_conn(message)

        self.assertEqual(len(self.mock_multicast_func.mock_calls), 1)
        got = self.mock_multicast_func.mock_calls[0].args[0]

        assert type(got) == Message
        assert got.event == "multicast"

        assert "target_conns" in got.header
        assert len(got.header["target_conns"]) == 1
        assert got.header["target_conns"][0] == message.header["sender"]

        assert type(got.payload) == TilesPayload
        assert got.payload.start_p.x == -2
        assert got.payload.start_p.y == 2
        assert got.payload.end_p.x == 2
        assert got.payload.end_p.y == -2
        assert got.payload.tiles == "df123df123df123er567er567"

    async def test_try_pointing(self):
        message = Message(
            event=PointEvent.TRY_POINTING,
            header={"sender": "ayo"},
            payload=TryPointingPayload(
                new_pointer=Point(0, 0),
                cursor_position=Point(0, 0),
                click_type="left",
                color=Color.BLUE
            )
        )

        await BoardHandler.receive_try_pointing(message)

        mock = self.mock_pointing_result_func
        self.assertEqual(len(mock.mock_calls), 1)
        self.assertEqual(len(mock.mock_calls[0].args), 1)

        message: Message[PointingResultPayload] = mock.mock_calls[0].args[0]
        self.assertEqual(message.event, PointEvent.POINTING_RESULT)

        self.assertEqual(len(message.header), 1)
        self.assertIn("receiver", message.header)
        self.assertEqual(message.header["receiver"], "ayo")

        self.assertEqual(type(message.payload), PointingResultPayload)
        self.assertEqual(message.payload.pointable, False)


if __name__ == "__main__":
    unittest.main()
