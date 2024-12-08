from cursor.data import Cursor, Color
from cursor.data.handler import CursorHandler
from cursor.event.handler import CursorEventHandler
from message import Message
from message.payload import (
    NewConnEvent,
    NewConnPayload,
    MyCursorPayload,
    CursorsPayload,
    PointEvent,
    PointingPayload,
    TryPointingPayload,
    PointingResultPayload,
    PointerSetPayload,
    ClickType,
    MoveEvent,
    MovingPayload,
    CheckMovablePayload,
    MovableResultPayload,
    MovedPayload,
    InteractionEvent,
    TileStateChangedPayload,
    YouDiedPayload,
    TileUpdatedPayload,
    ConnClosedPayload,
    CursorQuitPayload,
    SetViewSizePayload
)
from .fixtures import setup_cursor_locations
import unittest
from unittest.mock import AsyncMock, patch
from board.data import Point, Tile

"""
CursorEventHandler Test
----------------------------
Test
✅ : test 통과
❌ : test 실패
🖊️ : test 작성
- new-conn-receiver
    - ✅| normal-case
        - ✅| without-cursors
        - 작성해야함
- pointing-receiver
    - ✅| normal-case
        - 작성 해야함
# - pointing_result-receiver
#     - 작성해야 함
- moving-receiver
    - ✅| normal-case
        - 작성 해야함
"""


class CursorEventHandler_NewConnReceiver_TestCase(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        CursorHandler.cursor_dict = {}
        CursorHandler.watchers = {}
        CursorHandler.watching = {}

    @patch("event.EventBroker.publish")
    async def test_new_conn_receive_without_cursors(self, mock: AsyncMock):
        """
        new-conn-receiver
        without-cursors

        description:
            주변에 다른 커서 없을 경우
        ----------------------------
        trigger event ->

        - new-conn : message[NewConnPayload]
            - header :
                - sender : conn_id
            - descrption :
                connection 연결

        ----------------------------
        publish event ->

        - multicast : message[MyCursorPayload]
            - header :
                - target_conns : [conn_id]
                - origin_event : my-cursor
            - descrption :
                생성된 커서 정보
        - multicast : message[CursorsPayload]
            - header :
                - target_conns : [conn_id]
                - origin_event : cursors
            - descrption :
                생성된 커서의 주변 커서 정보
        - multicast : message[CursorsPayload]
            - header :
                - target_conns : [conn_id의 주변 커서 id]
                - origin_event : cursors
            - descrption :
                주변 커서에게 생성된 커서 정보
        ----------------------------
        """

        # 초기 커서 셋팅
        CursorHandler.cursor_dict = {}

        # 생성될 커서 값
        expected_conn_id = "example"
        expected_height = 100
        expected_width = 100

        # trigger message 생성
        message = Message(
            event=NewConnEvent.NEW_CONN,
            payload=NewConnPayload(
                conn_id=expected_conn_id,
                width=expected_width,
                height=expected_height
            )
        )

        # trigger event
        await CursorEventHandler.receive_new_conn(message)

        # 호출 여부
        self.assertEqual(len(mock.mock_calls), 1)
        got: Message[MyCursorPayload] = mock.mock_calls[0].args[0]

        # message 확인
        self.assertEqual(type(got), Message)
        # message.event
        self.assertEqual(got.event, "multicast")
        # message.header
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], expected_conn_id)
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], NewConnEvent.MY_CURSOR)

        # message.payload
        self.assertEqual(type(got.payload), MyCursorPayload)
        self.assertIsNone(got.payload.pointer)
        self.assertEqual(got.payload.position.x, 0)
        self.assertEqual(got.payload.position.y, 0)
        self.assertIn(got.payload.color, Color)

    @patch("event.EventBroker.publish")
    async def test_receive_new_conn_with_cursors(self, mock: AsyncMock):
        # /docs/example/cursor-location.png
        # But B is at 0,0
        CursorHandler.cursor_dict = {
            "A": Cursor(
                conn_id="A",
                position=Point(-3, 3),
                pointer=None,
                height=6,
                width=6,
                # color 중요. 이따 비교에 써야 함.
                color=Color.RED,
                revive_at=None
            ),
            "C": Cursor(
                conn_id="C",
                position=Point(2, -1),
                pointer=None,
                height=4,
                width=4,
                # color 중요.
                color=Color.BLUE,
                revive_at=None
            )
        }

        original_cursors_len = 2
        original_cursors = [c.conn_id for c in list(CursorHandler.cursor_dict.values())]

        new_conn_id = "B"
        height = 7
        width = 7

        message = Message(
            event=NewConnEvent.NEW_CONN,
            payload=NewConnPayload(
                conn_id=new_conn_id,
                width=height,
                height=width
            )
        )

        await CursorEventHandler.receive_new_conn(message)

        # publish 횟수
        self.assertEqual(len(mock.mock_calls), 3)

        # my-cursor
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # target_conns 나인지 확인
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], new_conn_id)
        # origin_event 확인
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], NewConnEvent.MY_CURSOR)
        # payload 확인
        self.assertEqual(type(got.payload), MyCursorPayload)
        self.assertEqual(got.payload.position, Point(0, 0))
        self.assertIsNone(got.payload.pointer)
        self.assertIn(got.payload.color, Color)

        my_color = got.payload.color

        # 커서 본인에게 보내는 cursors
        got = mock.mock_calls[1].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # target_conns 나인지 확인
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], new_conn_id)
        # origin_event 확인
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], NewConnEvent.CURSORS)
        # payload 확인
        self.assertEqual(type(got.payload), CursorsPayload)
        self.assertEqual(len(got.payload.cursors), 2)
        self.assertEqual(got.payload.cursors[0].color, Color.RED)
        self.assertEqual(got.payload.cursors[1].color, Color.BLUE)

        # 다른 커서들에게 보내는 cursors
        got = mock.mock_calls[2].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # target_conns 필터링 잘 됐는지 확인
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), original_cursors_len)
        self.assertEqual(set(got.header["target_conns"]), set(original_cursors))
        # origin_event 확인
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], NewConnEvent.CURSORS)
        # payload 확인
        self.assertEqual(type(got.payload), CursorsPayload)
        self.assertEqual(len(got.payload.cursors), 1)
        self.assertEqual(got.payload.cursors[0].color, my_color)

        # 연관관계 확인
        b_watching_list = CursorHandler.get_watching(new_conn_id)
        self.assertEqual(len(b_watching_list), original_cursors_len)

        b_watcher_list = CursorHandler.get_watchers(new_conn_id)
        self.assertEqual(len(b_watcher_list), original_cursors_len)


class CursorEventHandler_PointingReceiver_TestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        curs = setup_cursor_locations()
        self.cur_a = curs[0]
        self.cur_b = curs[1]
        self.cur_c = curs[2]

    def tearDown(self):
        CursorHandler.cursor_dict = {}
        CursorHandler.watchers = {}
        CursorHandler.watching = {}

    @patch("event.EventBroker.publish")
    async def test_receive_pointing(self, mock: AsyncMock):
        # TODO: out of bounds 테스트
        click_type = ClickType.GENERAL_CLICK
        pointer = Point(0, 0)

        message = Message(
            event=PointEvent.POINTING,
            header={"sender": self.cur_a.conn_id},
            payload=PointingPayload(
                click_type=click_type,
                position=pointer
            )
        )

        await CursorEventHandler.receive_pointing(message)

        # try-pointing 발행하는지 확인
        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.TRY_POINTING)

        # sender 확인
        self.assertIn("sender", got.header)
        self.assertEqual(type(got.header["sender"]), str)
        self.assertEqual(got.header["sender"], self.cur_a.conn_id)

        # payload 확인
        self.assertEqual(type(got.payload), TryPointingPayload)
        self.assertEqual(got.payload.click_type, click_type)
        self.assertEqual(got.payload.color, self.cur_a.color)
        self.assertEqual(got.payload.new_pointer, pointer)

    @patch("event.EventBroker.publish")
    async def test_receive_pointing_dead(self, mock: AsyncMock):
        from datetime import datetime
        self.cur_a.revive_at = datetime(year=2200, month=1, day=1, hour=0, minute=0, second=0)

        click_type = ClickType.GENERAL_CLICK
        pointer = Point(0, 0)

        message = Message(
            event=PointEvent.POINTING,
            header={"sender": self.cur_a.conn_id},
            payload=PointingPayload(
                click_type=click_type,
                position=pointer
            )
        )

        await CursorEventHandler.receive_pointing(message)

        mock.assert_not_called()

    @patch("event.EventBroker.publish")
    async def test_receive_pointing_result_pointable(self, mock: AsyncMock):
        origin_pointer = self.cur_a.pointer
        pointer = Point(1, 0)
        message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": self.cur_a.conn_id},
            payload=PointingResultPayload(
                pointer=pointer,
                pointable=True
            )
        )

        await CursorEventHandler.receive_pointing_result(message)

        # pointer-set 발행하는지 확인
        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.POINTER_SET)

        # target_conns -> 본인 + B 에게 보내는지 확인
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 2)
        self.assertIn("A", got.header["target_conns"])
        self.assertIn("B", got.header["target_conns"])

        # payload 확인
        self.assertEqual(type(got.payload), PointerSetPayload)
        self.assertEqual(got.payload.origin_position, origin_pointer)
        self.assertEqual(got.payload.color, self.cur_a.color)
        self.assertEqual(got.payload.new_position, pointer)

        self.assertEqual(self.cur_a.pointer, pointer)

    @patch("event.EventBroker.publish")
    async def test_receive_pointing_result_not_pointable(self, mock: AsyncMock):
        origin_pointer = Point(0, 0)
        self.cur_a.pointer = origin_pointer
        pointer = Point(1, 0)

        message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": self.cur_a.conn_id},
            payload=PointingResultPayload(
                pointer=pointer,
                pointable=False
            )
        )

        await CursorEventHandler.receive_pointing_result(message)

        # pointer-set 발행하는지 확인
        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.POINTER_SET)

        # target_conns -> 본인 + B 에게 보내는지 확인
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 2)
        self.assertIn("A", got.header["target_conns"])
        self.assertIn("B", got.header["target_conns"])

        # payload 확인
        self.assertEqual(type(got.payload), PointerSetPayload)
        self.assertEqual(got.payload.origin_position, origin_pointer)
        self.assertEqual(got.payload.color, self.cur_a.color)
        self.assertIsNone(got.payload.new_position)

        # 포인터 사라짐
        self.assertIsNone(self.cur_a.pointer)

    @patch("event.EventBroker.publish")
    async def test_receive_pointing_result_pointable_no_original_pointer(self, mock: AsyncMock):
        pointer = Point(1, 0)
        message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": self.cur_a.conn_id},
            payload=PointingResultPayload(
                pointer=pointer,
                pointable=True,
            )
        )

        await CursorEventHandler.receive_pointing_result(message)

        # pointer-set 발행하는지 확인
        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.POINTER_SET)

        # target_conns -> 본인 + B 에게 보내는지 확인
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 2)
        self.assertIn("A", got.header["target_conns"])
        self.assertIn("B", got.header["target_conns"])

        # payload 확인
        self.assertEqual(type(got.payload), PointerSetPayload)
        self.assertIsNone(got.payload.origin_position)
        self.assertEqual(got.payload.color, self.cur_a.color)
        self.assertEqual(got.payload.new_position, pointer)

    @patch("event.EventBroker.publish")
    async def test_receive_pointing_result_not_pointable_no_original_pointer(self, mock: AsyncMock):
        pointer = Point(1, 0)
        message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": self.cur_a.conn_id},
            payload=PointingResultPayload(
                pointer=pointer,
                pointable=False,
            )
        )

        await CursorEventHandler.receive_pointing_result(message)

        # 스킵하는지 확인
        mock.assert_not_called()
        self.assertNotEqual(self.cur_a.pointer, pointer)


class CursorEventHandler_MovingReceiver_TestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        curs = setup_cursor_locations()
        self.cur_a = curs[0]
        self.cur_b = curs[1]
        self.cur_c = curs[2]

    def tearDown(self):
        CursorHandler.cursor_dict = {}
        CursorHandler.watchers = {}
        CursorHandler.watching = {}

    @patch("event.EventBroker.publish")
    async def test_receive_moving(self, mock: AsyncMock):
        """
        TODO: 테스트 케이스
        1. 자기 자신 위치로 이동
        2. 주변 8칸 벗어나게 이동
        """
        message = Message(
            event=MoveEvent.MOVING,
            header={"sender": self.cur_a.conn_id},
            payload=CheckMovablePayload(
                position=Point(
                    # 위로 한칸 이동
                    x=self.cur_a.position.x,
                    y=self.cur_a.position.y + 1,
                )
            )
        )

        await CursorEventHandler.receive_moving(message)

        # check-movable 이벤트 발행 확인
        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, MoveEvent.CHECK_MOVABLE)

        # sender 보냈는지 확인
        self.assertIn("sender", got.header)
        self.assertEqual(type(got.header["sender"]), str)
        self.assertEqual(got.header["sender"], self.cur_a.conn_id)

        # 새로운 위치에 대해 check-movable 발행하는지 확인
        self.assertEqual(type(got.payload), CheckMovablePayload)
        self.assertEqual(got.payload.position, message.payload.position)

    @patch("event.EventBroker.publish")
    async def test_receive_movable_result_not_movable(self, mock: AsyncMock):
        message = Message(
            event=MoveEvent.MOVABLE_RESULT,
            header={"receiver": self.cur_a.conn_id},
            payload=MovableResultPayload(
                movable=False,
                position=Point(0, 0)
            )
        )

        await CursorEventHandler.receive_movable_result(message)

        mock.assert_not_called()

    @patch("event.EventBroker.publish")
    async def test_receive_movable_result_a_up(self, mock: AsyncMock):
        """
        A가 한 칸 위로 이동.
        B, C에게 move 이벤트가 전달되고, B의 시야에서 사라진다.
        """
        original_position = self.cur_a.position
        message = Message(
            event=MoveEvent.MOVABLE_RESULT,
            header={"receiver": self.cur_a.conn_id},
            payload=MovableResultPayload(
                movable=True,
                position=Point(
                    x=self.cur_a.position.x,
                    y=self.cur_a.position.y + 1,
                )
            )
        )

        await CursorEventHandler.receive_movable_result(message)

        # moved 이벤트만 발행됨
        self.assertEqual(len(mock.mock_calls), 1)

        # moved
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], MoveEvent.MOVED)
        # target_conns 확인, [B]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertIn("B", got.header["target_conns"])
        # payload 확인
        self.assertEqual(type(got.payload), MovedPayload)
        self.assertEqual(got.payload.origin_position, original_position)
        self.assertEqual(got.payload.new_position, message.payload.position)
        self.assertEqual(got.payload.color, self.cur_a.color)

        # watcher 관계 확인
        a_watchings = CursorHandler.get_watching("A")
        self.assertEqual(len(a_watchings), 1)
        self.assertIn("C", a_watchings)

        a_watchers = CursorHandler.get_watchers("A")
        self.assertEqual(len(a_watchers), 0)

        b_watchings = CursorHandler.get_watching("B")
        self.assertEqual(len(b_watchings), 1)
        self.assertIn("C", b_watchings)

    @patch("event.EventBroker.publish")
    async def test_receive_movable_result_b_up_right(self, mock: AsyncMock):
        """
        B가 한 칸 위, 한 칸 오른쪽로 이동.
        A, C의 뷰에 B가 추가된다.
        """
        original_position = self.cur_b.position
        message = Message(
            event=MoveEvent.MOVABLE_RESULT,
            header={"receiver": self.cur_b.conn_id},
            payload=MovableResultPayload(
                movable=True,
                position=Point(
                    x=self.cur_b.position.x + 1,
                    y=self.cur_b.position.y + 1,
                )
            )
        )

        await CursorEventHandler.receive_movable_result(message)

        # cursors 이벤트만 발행됨
        self.assertEqual(len(mock.mock_calls), 1)

        # cursors
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], NewConnEvent.CURSORS)
        # target_conns 확인, [A, C]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 2)
        self.assertIn("A", got.header["target_conns"])
        self.assertIn("C", got.header["target_conns"])
        # payload 확인, B의 정보
        self.assertEqual(type(got.payload), CursorsPayload)
        self.assertEqual(len(got.payload.cursors), 1)
        self.assertEqual(got.payload.cursors[0].position, message.payload.position)
        self.assertEqual(got.payload.cursors[0].pointer, self.cur_b.pointer)
        self.assertEqual(got.payload.cursors[0].color, self.cur_b.color)

        # watcher 관계 확인
        b_watchers = CursorHandler.get_watchers("B")
        self.assertEqual(len(b_watchers), 2)
        self.assertIn("A", b_watchers)
        self.assertIn("C", b_watchers)

        a_watchings = CursorHandler.get_watching("A")
        self.assertEqual(len(a_watchings), 2)
        self.assertIn("B", a_watchings)
        self.assertIn("C", a_watchings)

        c_watchings = CursorHandler.get_watching("C")
        self.assertEqual(len(c_watchings), 1)
        self.assertIn("B", c_watchings)

    @patch("event.EventBroker.publish")
    async def test_receive_movable_result_c_left(self, mock: AsyncMock):
        """
        C가 한 칸 왼쪽으로 이동.
        C의 뷰에 A, B가 추가되고, A, B에 move가 발행된다.
        """
        original_position = self.cur_c.position
        message = Message(
            event=MoveEvent.MOVABLE_RESULT,
            header={"receiver": self.cur_c.conn_id},
            payload=MovableResultPayload(
                movable=True,
                position=Point(
                    x=self.cur_c.position.x - 1,
                    y=self.cur_c.position.y,
                )
            )
        )

        await CursorEventHandler.receive_movable_result(message)

        # cursors, moved 이벤트 발행됨
        self.assertEqual(len(mock.mock_calls), 2)

        # cursors
        got = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], NewConnEvent.CURSORS)
        # target_conns 확인, [C]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertIn("C", got.header["target_conns"])
        # payload 확인, A, B의 정보
        self.assertEqual(type(got.payload), CursorsPayload)
        self.assertEqual(len(got.payload.cursors), 2)
        self.assertEqual(got.payload.cursors[0].position, self.cur_a.position)
        self.assertEqual(got.payload.cursors[0].pointer, self.cur_a.pointer)
        self.assertEqual(got.payload.cursors[0].color, self.cur_a.color)
        self.assertEqual(got.payload.cursors[1].position, self.cur_b.position)
        self.assertEqual(got.payload.cursors[1].pointer, self.cur_b.pointer)
        self.assertEqual(got.payload.cursors[1].color, self.cur_b.color)

        # moved
        got = mock.mock_calls[1].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], MoveEvent.MOVED)
        # target_conns 확인, [A, B]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 2)
        self.assertIn("A", got.header["target_conns"])
        self.assertIn("B", got.header["target_conns"])
        # payload 확인
        self.assertEqual(type(got.payload), MovedPayload)
        self.assertEqual(got.payload.origin_position, original_position)
        self.assertEqual(got.payload.new_position, message.payload.position)
        self.assertEqual(got.payload.color, self.cur_c.color)

        # watcher 관계 확인
        c_watchings = CursorHandler.get_watching("C")
        self.assertEqual(len(c_watchings), 2)
        self.assertIn("A", c_watchings)
        self.assertIn("B", c_watchings)


class CursorEventHandler_TileStateChanged_TestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        curs = setup_cursor_locations()
        self.cur_a = curs[0]
        self.cur_b = curs[1]
        self.cur_c = curs[2]

    def tearDown(self):
        CursorHandler.cursor_dict = {}
        CursorHandler.watchers = {}
        CursorHandler.watching = {}

    @patch("event.EventBroker.publish")
    async def test_receive_tile_state_changed(self, mock: AsyncMock):
        position = Point(-4, -3)
        tile = Tile.from_int(0b00100111)  # not open, flag, 7

        message: Message[TileStateChangedPayload] = Message(
            event=InteractionEvent.TILE_STATE_CHANGED,
            payload=TileStateChangedPayload(
                position=position,
                tile=tile
            )
        )

        await CursorEventHandler.receive_tile_state_changed(message)

        # tile-updated 발행 확인
        self.assertEqual(len(mock.mock_calls), 1)

        # tile-updated
        got: Message[TileUpdatedPayload] = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], InteractionEvent.TILE_UPDATED)
        # target_conns 확인, [A, B]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 2)
        self.assertIn("A", got.header["target_conns"])
        self.assertIn("B", got.header["target_conns"])
        # payload 확인
        self.assertEqual(type(got.payload), TileUpdatedPayload)
        self.assertEqual(got.payload.position, position)
        self.assertEqual(got.payload.tile, tile.copy(hide_info=True))

    @patch("event.EventBroker.publish")
    async def test_receive_tile_state_changed_mine_boom(self, mock: AsyncMock):
        position = Point(-4, -3)
        tile = Tile.from_int(0b11000000)  # open, mine

        message: Message[TileStateChangedPayload] = Message(
            event=InteractionEvent.TILE_STATE_CHANGED,
            payload=TileStateChangedPayload(
                position=position,
                tile=tile
            )
        )

        await CursorEventHandler.receive_tile_state_changed(message)

        # tile-updated, you-died 발행 확인
        self.assertEqual(len(mock.mock_calls), 2)

        # tile-updated
        got: Message[TileUpdatedPayload] = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], InteractionEvent.TILE_UPDATED)
        # target_conns 확인, [A, B]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 2)
        self.assertIn("A", got.header["target_conns"])
        self.assertIn("B", got.header["target_conns"])
        # payload 확인
        self.assertEqual(type(got.payload), TileUpdatedPayload)
        self.assertEqual(got.payload.position, position)
        self.assertEqual(got.payload.tile.data, tile.data)

        # you-died
        got: Message[YouDiedPayload] = mock.mock_calls[1].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")

        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], InteractionEvent.YOU_DIED)
        # target_conns 확인, [B]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertIn("B", got.header["target_conns"])
        # payload 확인
        self.assertEqual(type(got.payload), YouDiedPayload)
        # TODO
        # datetime.now mocking 후 test
        # self.assertEqual(got.payload.revive_at, something)


class CursorEventHandler_ConnClosed_TestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        curs = setup_cursor_locations()
        self.cur_a = curs[0]
        self.cur_b = curs[1]
        self.cur_c = curs[2]

    def tearDown(self):
        CursorHandler.cursor_dict = {}
        CursorHandler.watchers = {}
        CursorHandler.watching = {}

    @patch("event.EventBroker.publish")
    async def test_receive_conn_closed(self, mock: AsyncMock):
        message = Message(
            event=NewConnEvent.CONN_CLOSED,
            header={"sender": self.cur_a.conn_id},
            payload=ConnClosedPayload()
        )

        await CursorEventHandler.receive_conn_closed(message)

        mock.assert_called_once()

        # cursor-quit
        got: Message[CursorQuitPayload] = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], NewConnEvent.CURSOR_QUIT)
        # target_conns 확인, [B]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertIn("B", got.header["target_conns"])
        # payload 확인
        self.assertEqual(type(got.payload), CursorQuitPayload)
        self.assertEqual(got.payload.position, self.cur_a.position)
        self.assertEqual(got.payload.pointer, self.cur_a.pointer)
        self.assertEqual(got.payload.color, self.cur_a.color)

        # watcher 관계 확인
        b_watchings = CursorHandler.get_watching("B")
        self.assertEqual(len(b_watchings), 1)
        self.assertIn("C", b_watchings)

        c_watchers = CursorHandler.get_watchers("C")
        self.assertEqual(len(c_watchers), 1)
        self.assertIn("B", c_watchers)

        # 커서 지워졌나 확인
        self.assertIsNone(CursorHandler.get_cursor(self.cur_a.conn_id))


class CursorEventHandler_SetViewSize_TestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        curs = setup_cursor_locations()
        self.cur_a = curs[0]
        self.cur_b = curs[1]
        self.cur_c = curs[2]

    def tearDown(self):
        CursorHandler.cursor_dict = {}
        CursorHandler.watchers = {}
        CursorHandler.watching = {}

    @patch("event.EventBroker.publish")
    async def test_receive_set_view_size_grow_shrink_both(self, mock: AsyncMock):
        message = Message(
            event=NewConnEvent.SET_VIEW_SIZE,
            header={"sender": self.cur_a.conn_id},
            payload=SetViewSizePayload(
                width=self.cur_a.width-2,
                height=self.cur_a.height+1
            )
        )

        await CursorEventHandler.receive_set_view_size(message)

        mock.assert_called_once()

        # cursors
        got: Message[CursorsPayload] = mock.mock_calls[0].args[0]
        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")
        # origin_event
        self.assertIn("origin_event", got.header)
        self.assertEqual(got.header["origin_event"], NewConnEvent.CURSORS)
        # target_conns 확인, [A]
        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertIn(self.cur_a.conn_id, got.header["target_conns"])
        # payload 확인
        self.assertEqual(type(got.payload), CursorsPayload)
        self.assertEqual(len(got.payload.cursors), 1)
        self.assertEqual(got.payload.cursors[0].color, self.cur_b.color)
        self.assertEqual(got.payload.cursors[0].position, self.cur_b.position)

        # watcher 관계 확인
        a_watching = CursorHandler.get_watching("A")
        self.assertEqual(len(a_watching), 1)
        self.assertIn("B", a_watching)

        b_watchers = CursorHandler.get_watchers("B")
        self.assertEqual(len(b_watchers), 1)
        self.assertIn("A", b_watchers)

    @patch("event.EventBroker.publish")
    async def test_receive_set_view_size_same(self, mock: AsyncMock):
        message = Message(
            event=NewConnEvent.SET_VIEW_SIZE,
            header={"sender": self.cur_a.conn_id},
            payload=SetViewSizePayload(
                width=self.cur_a.width,
                height=self.cur_a.height
            )
        )

        await CursorEventHandler.receive_set_view_size(message)

        mock.assert_not_called()

        # watcher 관계 확인
        a_watching = CursorHandler.get_watching("A")
        self.assertEqual(len(a_watching), 1)
        self.assertIn("C", a_watching)

        b_watchers = CursorHandler.get_watchers("B")
        self.assertEqual(len(b_watchers), 0)

    @patch("event.EventBroker.publish")
    async def test_receive_set_view_size_shrink(self, mock: AsyncMock):
        message = Message(
            event=NewConnEvent.SET_VIEW_SIZE,
            header={"sender": self.cur_b.conn_id},
            payload=SetViewSizePayload(
                width=self.cur_b.width,
                height=self.cur_b.height-1
            )
        )

        await CursorEventHandler.receive_set_view_size(message)

        mock.assert_not_called()

        # watcher 관계 확인
        b_watching = CursorHandler.get_watching("B")
        self.assertEqual(len(b_watching), 1)
        self.assertIn("C", b_watching)

        a_watchers = CursorHandler.get_watchers("A")
        self.assertEqual(len(a_watchers), 0)


if __name__ == "__main__":
    unittest.main()
