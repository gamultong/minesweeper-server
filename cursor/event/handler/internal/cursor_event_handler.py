from cursor.data import Cursor
from cursor.data.handler import CursorHandler
from board import Point
from event import EventBroker
from message import Message
from message.payload import NewConnPayload, MyCursorPayload, CursorsPayload, CursorPayload, NewConnEvent, PointingPayload, TryPointingPayload, PointingResultPayload, PointerSetPayload, PointEvent


class CursorEventHandler:
    @EventBroker.add_receiver(NewConnEvent.NEW_CONN)
    @staticmethod
    async def receive_new_conn(message: Message[NewConnPayload]):
        cursor = CursorHandler.create(message.payload.conn_id)
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
            nearby_cursors_message = Message(
                event="multicast",
                header={"target_conns": [message.payload.conn_id],
                        "origin_event": NewConnEvent.CURSORS},
                payload=CursorsPayload(
                    cursors=[
                        CursorPayload(cur.position, cur.pointer, cur.color) for cur in cursors_in_range
                    ]
                )
            )

            await EventBroker.publish(nearby_cursors_message)

        cursors_with_view_including = CursorHandler.view_includes(cursor.position, cursor.conn_id)
        if len(cursors_with_view_including) > 0:
            cursor_appeared_message = Message(
                event="multicast",
                header={"target_conns": [cursor.conn_id for cursor in cursors_with_view_including],
                        "origin_event": NewConnEvent.CURSORS},
                payload=CursorsPayload(
                    cursors=[CursorPayload(cursor.position, cursor.pointer, cursor.color)]
                )
            )

            await EventBroker.publish(cursor_appeared_message)

    @EventBroker.add_receiver(PointEvent.POINTING)
    @staticmethod
    async def receive_pointing(message: Message[PointingPayload]):
        sender = message.header["sender"]

        # TODO: get_cursor 메서드 만들기
        cursor = CursorHandler.cursor_dict[sender]
        new_pointer = message.payload.position

        # 뷰 바운더리 안에서 포인팅하는지 확인
        # TODO: 커서 내부 메서드로 바꾸기
        left_up_edge = Point(cursor.position.x - cursor.width, cursor.position.y + cursor.height)
        right_down_edge = Point(cursor.position.x + cursor.width, cursor.position.y - cursor.height)

        if \
                new_pointer.x < left_up_edge.x or \
                new_pointer.x > right_down_edge.x or \
                new_pointer.y > left_up_edge.y or \
                new_pointer.y < right_down_edge.y:
            # TODO: 예외 처리?
            pass

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

    @EventBroker.add_receiver(PointEvent.POINTING_RESULT)
    @staticmethod
    async def receive_pointing_result(message: Message[PointingResultPayload]):
        receiver = message.header["receiver"]

        # TODO: 여기도 마찬가지
        cursor = CursorHandler.cursor_dict[receiver]

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
