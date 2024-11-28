from cursor import Cursor, Color
from cursor.manager import CursorManager
from message import Message
from message.payload import NewConnEvent, NewCursorPayload, MyCursorPayload, PointEvent, PointingPayload, TryPointingPayload, PointingResultPayload, PointerSetPayload, ClickType
import unittest
from unittest.mock import AsyncMock, patch
from board import Point

"""
BoardHandler Test
----------------------------
Test
✅ : test 통과
❌ : test 실패 
🖊️ : test 작성

- CursorManager
    - 작성 해야함
- new-conn-receiver
    - ✅| normal-case
        - ✅| without-cursors
        - 작성해야함
- pointing-recieve
    - ✅| normal-case
        - 작성 해야함
"""


def get_cur(conn_id):
    return Cursor(
        conn_id=conn_id,
        position=Point(0, 0),
        pointer=None,
        new_pointer=None,
        height=10,
        width=10,
        color=Color.BLUE
    )


class CursorManagerTestCase(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        CursorManager.cursor_dict = {
            "example_1": get_cur("example_1"),
            "example_2": get_cur("example_2"),
            "example_3": get_cur("example_3")
        }

    def tearDown(self):
        CursorManager.cursor_dict = {}

    def test_create(self):
        conn_id = "example_conn_id"
        CursorManager.create(conn_id)

        self.assertIn(conn_id, CursorManager.cursor_dict)
        self.assertEqual(type(CursorManager.cursor_dict[conn_id]), Cursor)
        self.assertEqual(CursorManager.cursor_dict[conn_id].conn_id, conn_id)

    def test_remove(self):
        CursorManager.remove("example_1")
        self.assertNotIn("example_1", CursorManager.cursor_dict)
        self.assertEqual(len(CursorManager.cursor_dict), 2)

    def test_exists_range(self):
        result = CursorManager.exists_range(Point(0, 0), Point(0, 0))

        self.assertEqual(len(result), 3)

    def test_view_includes(self):
        result = CursorManager.view_includes(Point(0, 0))

        self.assertEqual(len(result), 3)


class CursorManager_NewConnReceiver_TestCase(unittest.IsolatedAsyncioTestCase):
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

        - multicast : message[NewCursorPayload]
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
        CursorManager.cursor_dict = {}

        # 생성될 커서 값
        expected_conn_id = "example"
        expected_height = 100
        expected_width = 100

        # trigger message 생성
        message = Message(
            event=NewConnEvent.NEW_CONN,
            payload=MyCursorPayload(
                conn_id=expected_conn_id,
                width=expected_width,
                height=expected_height
            )
        )

        # trigger event
        await CursorManager.receive_new_conn(message)

        # 호출 여부
        self.assertEqual(len(mock.mock_calls), 1)
        got: Message[NewCursorPayload] = mock.mock_calls[0].args[0]

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
        self.assertEqual(type(got.payload), NewCursorPayload)
        self.assertIsNone(got.payload.pointer)
        self.assertEqual(got.payload.position.x, 0)
        self.assertEqual(got.payload.position.y, 0)
        self.assertIn(got.payload.color, Color)

    @patch("event.EventBroker.publish")
    async def test_receive_new_conn_with_cursors(self, mock: AsyncMock):
        # TODO: 쿼리 로직 바뀌면 이것도 같이 바꿔야 함.
        CursorManager.cursor_dict = {
            "some id": Cursor.create("some id")
        }

        expected_conn_id = "example"
        expected_height = 100
        expected_width = 100

        message = Message(
            event=NewConnEvent.NEW_CONN,
            payload=MyCursorPayload(
                conn_id=expected_conn_id,
                width=expected_width,
                height=expected_height
            )
        )

        await CursorManager.receive_new_conn(message)

        self.assertEqual(len(mock.mock_calls), 3)
        got = mock.mock_calls[0].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")

        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], expected_conn_id)

        got = mock.mock_calls[1].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")

        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], expected_conn_id)

        got = mock.mock_calls[2].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, "multicast")

        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), len(CursorManager.cursor_dict) - 1)
        self.assertEqual(set(got.header["target_conns"]), set([c.conn_id for c in CursorManager.cursor_dict.values() if c.conn_id != expected_conn_id]))


class CursorManager_PointingReceiver_TestCase(unittest.IsolatedAsyncioTestCase):
    @patch("event.EventBroker.publish")
    async def test_receive_pointing(self, mock: AsyncMock):
        expected_conn_id = "example"
        expected_width = 100
        expected_height = 100

        cursor = Cursor.create(conn_id=expected_conn_id)
        cursor.set_size(expected_width, expected_height)

        CursorManager.cursor_dict = {
            expected_conn_id: cursor
        }

        click_type = ClickType.GENERAL_CLICK

        message = Message(
            event=PointEvent.POINTING,
            header={"sender": expected_conn_id},
            payload=PointingPayload(
                click_type=click_type,
                position=Point(0, 0)
            )
        )

        await CursorManager.receive_pointing(message)

        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.TRY_POINTING)

        self.assertIn("sender", got.header)
        self.assertEqual(type(got.header["sender"]), str)
        self.assertEqual(got.header["sender"], expected_conn_id)

        self.assertEqual(type(got.payload), TryPointingPayload)
        self.assertEqual(got.payload.click_type, click_type)
        self.assertEqual(got.payload.cursor_position, cursor.position)
        self.assertEqual(got.payload.color, cursor.color)
        self.assertEqual(got.payload.new_pointer, Point(0, 0))

        self.assertEqual(cursor.new_pointer, message.payload.position)

    @patch("event.EventBroker.publish")
    async def test_receive_pointing_result_pointable(self, mock: AsyncMock):
        expected_conn_id = "example"

        cursor = Cursor.create(conn_id=expected_conn_id)
        cursor.pointer = Point(0, 0)
        cursor.new_pointer = Point(0, 0)

        CursorManager.cursor_dict = {
            expected_conn_id: cursor
        }

        message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": expected_conn_id},
            payload=PointingResultPayload(
                pointable=True,
            )
        )

        await CursorManager.receive_pointing_result(message)

        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.POINTER_SET)

        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], expected_conn_id)

        self.assertEqual(type(got.payload), PointerSetPayload)
        self.assertEqual(got.payload.origin_position, Point(0, 0))
        self.assertEqual(got.payload.color, cursor.color)
        self.assertEqual(got.payload.new_position, Point(0, 0))

        self.assertEqual(cursor.pointer, got.payload.new_position)
        self.assertIsNone(cursor.new_pointer)

    @patch("event.EventBroker.publish")
    async def test_receive_pointing_result_not_pointable(self, mock: AsyncMock):
        expected_conn_id = "example"

        cursor = Cursor.create(conn_id=expected_conn_id)
        cursor.pointer = Point(0, 0)

        CursorManager.cursor_dict = {
            expected_conn_id: cursor
        }

        message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": expected_conn_id},
            payload=PointingResultPayload(
                pointable=False,
            )
        )

        await CursorManager.receive_pointing_result(message)

        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.POINTER_SET)

        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], expected_conn_id)

        self.assertEqual(type(got.payload), PointerSetPayload)
        self.assertEqual(got.payload.origin_position, Point(0, 0))
        self.assertEqual(got.payload.color, cursor.color)
        self.assertIsNone(got.payload.new_position)

    @patch("event.EventBroker.publish")
    async def test_receive_pointing_result_pointable_no_original_pointer(self, mock: AsyncMock):
        expected_conn_id = "example"

        cursor = Cursor.create(conn_id=expected_conn_id)
        cursor.new_pointer = Point(0, 0)

        CursorManager.cursor_dict = {
            expected_conn_id: cursor
        }

        message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": expected_conn_id},
            payload=PointingResultPayload(
                pointable=True,
            )
        )

        await CursorManager.receive_pointing_result(message)

        mock.assert_called_once()
        got = mock.mock_calls[0].args[0]

        self.assertEqual(type(got), Message)
        self.assertEqual(got.event, PointEvent.POINTER_SET)

        self.assertIn("target_conns", got.header)
        self.assertEqual(len(got.header["target_conns"]), 1)
        self.assertEqual(got.header["target_conns"][0], expected_conn_id)

        self.assertEqual(type(got.payload), PointerSetPayload)
        self.assertIsNone(got.payload.origin_position)
        self.assertEqual(got.payload.color, cursor.color)
        self.assertEqual(got.payload.new_position, Point(0, 0))


if __name__ == "__main__":
    unittest.main()
