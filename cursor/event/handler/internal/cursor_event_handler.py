from cursor.data import Cursor
from cursor.data.handler import CursorHandler
from board.data import Point
from event import EventBroker
from message import Message
from message.payload import NewConnPayload, MyCursorPayload, CursorsPayload, CursorPayload, NewConnEvent, PointingPayload, TryPointingPayload, PointingResultPayload, PointerSetPayload, PointEvent, MoveEvent, MovingPayload, CheckMovablePayload


class CursorEventHandler:
    @EventBroker.add_receiver(NewConnEvent.NEW_CONN)
    @staticmethod
    async def receive_new_conn(message: Message[NewConnPayload]):
        cursor = CursorHandler.create_cursor(message.payload.conn_id)
        cursor.set_size(message.payload.width, message.payload.height)

        new_cursor_message = Message(
            event="multicast",
            header={"target_conns": [cursor.conn_id],
                    "origin_event": NewConnEvent.MY_CURSOR},
            payload=MyCursorPayload(
                position=cursor.position,
                pointer=cursor.pointer,
                color=cursor.color
            )
        )

        await EventBroker.publish(new_cursor_message)

        start_p = Point(
            x=cursor.position.x - cursor.width,
            y=cursor.position.y + cursor.height
        )
        end_p = Point(
            x=cursor.position.x + cursor.width,
            y=cursor.position.y - cursor.height
        )

        cursors_in_range = CursorHandler.exists_range(start_p, end_p, cursor.conn_id)
        if len(cursors_in_range) > 0:
            # 내가 보고있는 커서들
            for other_cursor in cursors_in_range:
                CursorHandler.add_watcher(watcher=cursor, watching=other_cursor)

            await publish_new_cursors_event(
                target_cursors=[cursor],
                cursors=cursors_in_range
            )

        cursors_with_view_including = CursorHandler.view_includes(cursor.position, cursor.conn_id)
        if len(cursors_with_view_including) > 0:
            # 나를 보고있는 커서들
            for other_cursor in cursors_with_view_including:
                CursorHandler.add_watcher(watcher=other_cursor, watching=cursor)

            await publish_new_cursors_event(
                target_cursors=cursors_with_view_including,
                cursors=[cursor]
            )

    @EventBroker.add_receiver(PointEvent.POINTING)
    @staticmethod
    async def receive_pointing(message: Message[PointingPayload]):
        sender = message.header["sender"]

        cursor = CursorHandler.get_cursor(sender)
        new_pointer = message.payload.position

        # 뷰 바운더리 안에서 포인팅하는지 확인
        if not cursor.check_in_view(new_pointer):
            # TODO: 예외 처리?
            raise "커서 뷰 바운더리 벗어난 곳에 포인팅함"

        message = Message(
            event=PointEvent.TRY_POINTING,
            header={"sender": sender},
            payload=TryPointingPayload(
                cursor_position=cursor.position,
                new_pointer=new_pointer,
                color=cursor.color,
                click_type=message.payload.click_type
            )
        )

        await EventBroker.publish(message)

    @EventBroker.add_receiver(MoveEvent.MOVING)
    @staticmethod
    async def receive_moving(message: Message[MovingPayload]):
        sender = message.header["sender"]

        cursor = CursorHandler.get_cursor(sender)

        new_position = message.payload.position

        if new_position == cursor.position:
            # TODO: 예외 처리
            raise "기존 위치와 같은 위치로 이동"

        if not cursor.check_interactable(new_position):
            raise "주변 8칸 벗어남"

        message = Message(
            event=MoveEvent.CHECK_MOVABLE,
            header={"sender": cursor.conn_id},
            payload=CheckMovablePayload(
                position=new_position
            )
        )

        await EventBroker.publish(message)

    @EventBroker.add_receiver(PointEvent.POINTING_RESULT)
    @staticmethod
    async def receive_pointing_result(message: Message[PointingResultPayload]):
        receiver = message.header["receiver"]

        cursor = CursorHandler.get_cursor(receiver)

        new_pointer = message.payload.pointer if message.payload.pointable else None
        origin_pointer = cursor.pointer
        cursor.pointer = new_pointer

        message = Message(
            event=PointEvent.POINTER_SET,
            header={"target_conns": [cursor.conn_id]},
            payload=PointerSetPayload(
                origin_position=origin_pointer,
                new_position=new_pointer,
                color=cursor.color,
            )
        )

        await EventBroker.publish(message)


async def publish_new_cursors_event(target_cursors: list[Cursor], cursors: list[Cursor]):
    message = Message(
        event="multicast",
        header={"target_conns": [cursor.conn_id for cursor in target_cursors],
                "origin_event": NewConnEvent.CURSORS},
        payload=CursorsPayload(
            cursors=[CursorPayload(cursor.position, cursor.pointer, cursor.color) for cursor in cursors]
        )
    )

    await EventBroker.publish(message)
