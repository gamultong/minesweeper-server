import unittest
from unittest.mock import AsyncMock, patch
from board.handler import BoardHandler
from message import Message
from message.payload import \
    FetchTilesPayload, TilesEvent, TilesPayload, NewConnEvent, NewConnPayload, TryPointingPayload, PointingResultPayload, PointEvent, ClickType, MoveEvent, CheckMovablePayload, MovableResultPayload
from board.test.fixtures import setup_board
from board import Point
from cursor import Color


"""
BoardHandler Test
----------------------------
Test
✅ : test 통과
❌ : test 실패 
🖊️ : test 작성

- fetch-tiles-receiver
    - ✅| normal-case
    - 🖊️| invaild-message
        - 🖊️| invaild-message-payload
        - 🖊️| no-sender
        - 🖊️| invaild-header
- new-conn-receiver
    - ✅| normal-case
- try-pointing-receiver
    - ✅| normal-case
- check-movable-receiver
    -  ✅| normal-case
"""


# fetch-tiles-receiver Test
class BoardHandler_FetchTilesReceiver_TestCase(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        setup_board()

    @patch("event.EventBroker.publish")
    async def test_fetch_tiles_receiver_normal_case(self, mock: AsyncMock):
        """
        fetch-tiles-receiver 
        normal-case
        ----------------------------
        trigger event ->

        - fetch-tiles : message[FetchTilesPayload]
            - header : 
                - sender : conn_id
            - descrption :
                econn_id의 tiles 정보 요청
        ----------------------------
        publish event ->

        - multicast : message[TilesPayload]
            - header :
                - target_conns : [conn_id]
                - origin_event : tiles
            - descrption :
                fetch-tiles의 대한 응답
        ----------------------------
        """

        # trigger message 생성
        message = Message(
            event=TilesEvent.FETCH_TILES,
            payload=FetchTilesPayload(Point(-2, 1), Point(1, -2)),
            header={"sender": "ayo"},

        )

        # trigger event
        await BoardHandler.receive_fetch_tiles(message)

        # 호출 여부
        mock.assert_called_once()
        got: Message[TilesPayload] = mock.mock_calls[0].args[0]

        # message 확인
        self.assertEqual(type(got), Message)
        # message.event
        self.assertEqual(got.event, "multicast")
        # message.header
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], message.header["sender"])
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], TilesEvent.TILES)

        # message.payload
        self.assertEqual(type(got.payload), TilesPayload)
        self.assertEqual(got.payload.start_p.x, -2)
        self.assertEqual(got.payload.start_p.y, 1)
        self.assertEqual(got.payload.end_p.x, 1)
        self.assertEqual(got.payload.end_p.y, -2)
        self.assertEqual(got.payload.tiles, "df12df12er56er56")

    @patch("event.EventBroker.publish")
    async def test_receive_new_conn(self, mock: AsyncMock):
        message = Message(
            event=NewConnEvent.NEW_CONN,
            header={"sender": "ayo"},
            payload=NewConnPayload(conn_id="not important", width=2, height=2)
        )

        await BoardHandler.receive_new_conn(message)

        mock.assert_called_once()
        got: Message[TilesPayload] = mock.mock_calls[0].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")

        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], message.header["sender"])

        self.assertEqual(type(got.payload), TilesPayload)
        self.assertEqual(got.payload.start_p.x, -2)
        self.assertEqual(got.payload.start_p.y, 2)
        self.assertEqual(got.payload.end_p.x, 2)
        self.assertEqual(got.payload.end_p.y, -2)
        self.assertEqual(got.payload.tiles, "df123df123df123er567er567")

    @patch("event.EventBroker.publish")
    async def test_try_pointing(self, mock: AsyncMock):
        # TODO: pointable한 것과 pointable하지 않은 것 테스트 나누기
        message = Message(
            event=PointEvent.TRY_POINTING,
            header={"sender": "ayo"},
            payload=TryPointingPayload(
                new_pointer=Point(0, 0),
                cursor_position=Point(0, 0),
                click_type=ClickType.GENERAL_CLICK,
                color=Color.BLUE
            )
        )

        await BoardHandler.receive_try_pointing(message)

        mock.assert_called_once()
        got: Message[PointingResultPayload] = mock.mock_calls[0].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.POINTING_RESULT)

        self.assertEqual(len(got.header), 1)
        self.assertIn("receiver", got.header)
        self.assertEqual(got.header["receiver"], "ayo")

        self.assertEqual(type(got.payload), PointingResultPayload)
        self.assertFalse(got.payload.pointable)

    @patch("event.EventBroker.publish")
    async def test_check_movable(self, mock: AsyncMock):
        # TODO: 위와 마찬가지로 movable한 것과 movable하지 않은 것 테스트 분리

        new_position = Point(0, 0)
        message = Message(
            event=MoveEvent.CHECK_MOVABLE,
            header={"sender": "ayo"},
            payload=CheckMovablePayload(
                position=new_position
            )
        )

        await BoardHandler.receive_check_movable(message)

        mock.assert_called_once()
        got: Message[MovableResultPayload] = mock.mock_calls[0].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, MoveEvent.MOVABLE_RESULT)

        self.assertEqual(len(got.header), 1)
        self.assertIn("receiver", got.header)
        self.assertEqual(got.header["receiver"], "ayo")

        self.assertEqual(type(got.payload), MovableResultPayload)
        self.assertEqual(got.payload.position, new_position)
        self.assertFalse(got.payload.movable)


if __name__ == "__main__":
    unittest.main()
