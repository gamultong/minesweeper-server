from cursor import Cursor
from board import Point
from event import EventBroker
from message import Message
from message.payload import NewConnPayload, NewCursorPayload, NearbyCursorPayload, CursorAppearedPayload, CursorPayload, NewConnEvent


class CursorManager:
    cursor_dict: dict[str, Cursor]

    @staticmethod
    def create(conn_id: str):
        cursor = Cursor.create(conn_id)
        CursorManager.cursor_dict[conn_id] = cursor

    @staticmethod
    def remove(conn_id: str):
        if conn_id in CursorManager.cursor_dict:
            del CursorManager.cursor_dict[conn_id]

    @staticmethod
    def exists_range(start: Point, end: Point) -> list[Cursor]:
        # 일단 broadcast. 추후 고쳐야 함.
        return list(CursorManager.cursor_dict.values())

    @staticmethod
    def view_includes(p: Point) -> list[Cursor]:
        # 일단 broadcast. 추후 고쳐야 함.
        return list(CursorManager.cursor_dict.values())

    @EventBroker.add_receiver(NewConnEvent.NEW_CONN)
    @staticmethod
    async def receiver_new_conn(message: Message[NewConnPayload]):
        CursorManager.create(message.payload.conn_id)

        cursor = CursorManager.cursor_dict[message.payload.conn_id]
        cursor.set_size(message.payload.width, message.payload.height)

        new_cursor_message = Message(
            event=NewConnEvent.MY_CURSOR,
            # ToDo
            # header = {
            #     "target_conns":[cursor.conn_id]
            # },
            payload=NewCursorPayload(
                position=cursor.position,
                pointer=cursor.pointer,
                color=cursor.color
            )
        )

        await EventBroker.publish(new_cursor_message)

        start_p = Point(
            cursor.position.x, - cursor.width,
            cursor.position.y, + cursor.height,
        )
        end_p = Point(
            cursor.position.x, + cursor.width,
            cursor.position.y, - cursor.height,
        )

        cursors_in_range = CursorManager.exists_range(start_p, end_p)
        if len(cursors_in_range) > 0:
            nearby_cursors_message = Message(
                event=NewConnEvent.NEARYBY_CURSORS,
                payload=NearbyCursorPayload(
                    cursors=[
                        CursorPayload(c.positoin, c.pointer, c.color) for c in cursors_in_range
                    ]
                )
            )

            await EventBroker.publish(nearby_cursors_message)

        cursors_with_view_including = CursorManager.view_includes(cursor.position)
        if len(cursors_with_view_including) > 0:
            cursor_appeared_message = Message(
                event=NewConnEvent.CURSOR_APPEARED,
                payload=CursorAppearedPayload(
                    position=cursor.position,
                    pointer=cursor.pointer,
                    color=cursor.color
                )
            )

            # TODO: 각 커서마다 발행
            await EventBroker.publish(cursor_appeared_message)
