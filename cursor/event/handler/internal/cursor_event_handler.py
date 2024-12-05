from cursor.data import Cursor
from cursor.data.handler import CursorHandler
from board.data import Point, Tile
from event import EventBroker
from message import Message
from datetime import datetime, timedelta
from message.payload import (
    NewConnPayload,
    MyCursorPayload,
    CursorsPayload,
    CursorPayload,
    NewConnEvent,
    PointingPayload,
    TryPointingPayload,
    PointingResultPayload,
    PointerSetPayload,
    PointEvent,
    MoveEvent,
    MovingPayload,
    CheckMovablePayload,
    MovableResultPayload,
    MovedPayload,
    InteractionEvent,
    TileStateChangedPayload,
    TileUpdatedPayload,
    YouDiedPayload,
    ConnClosedPayload,
    CursorQuitPayload
)


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

        # 커서 부활시간 확인
        if cursor.revive_at is not None:
            if cursor.revive_at >= datetime.now():
                return
            cursor.revive_at = None

        # 뷰 바운더리 안에서 포인팅하는지 확인
        if not cursor.check_in_view(new_pointer):
            # TODO: 예외 처리?
            raise "커서 뷰 바운더리 벗어난 곳에 포인팅함"

        message = Message(
            event=PointEvent.TRY_POINTING,
            header={"sender": sender},
            payload=TryPointingPayload(
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

        cursor = CursorHandler.get_cursor(receiver)

        new_pointer = message.payload.pointer if message.payload.pointable else None
        origin_pointer = cursor.pointer
        cursor.pointer = new_pointer

        # TODO: 이거 본인 보고있는 커서들한테 보내야 함.
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

    @EventBroker.add_receiver(MoveEvent.MOVABLE_RESULT)
    @staticmethod
    async def receive_movable_result(message: Message[MovableResultPayload]):
        receiver = message.header["receiver"]

        cursor = CursorHandler.get_cursor(receiver)

        if not message.payload.movable:
            # TODO: 사용자에게 알리기?
            return

        new_position = message.payload.position
        original_position = cursor.position

        cursor.position = new_position

        # TODO: 새로운 방식으로 커서들 찾기. 최적화하기.
        # set을 사용하면 제약이 있음.

        # 새로운 뷰의 커서들 찾기
        top_left = Point(cursor.position.x - cursor.width, cursor.position.y + cursor.height)
        bottom_right = Point(cursor.position.x + cursor.width, cursor.position.y - cursor.height)
        cursors_in_view = CursorHandler.exists_range(top_left, bottom_right, cursor.conn_id)

        original_watching_ids = CursorHandler.get_watching(cursor_id=cursor.conn_id)
        original_watchings = [CursorHandler.get_cursor(id) for id in original_watching_ids]

        if len(original_watchings) > 0:
            # 범위 벗어난 커서들 연관관계 해제
            for watching in original_watchings:
                in_view = cursor.check_in_view(watching.position)
                if not in_view:
                    CursorHandler.remove_watcher(watcher=cursor, watching=other_cursor)

        new_watchings = list(filter(lambda c: c.conn_id not in original_watching_ids, cursors_in_view))
        if len(new_watchings) > 0:
            # 새로운 watching 커서들 연관관계 설정
            for other_cursor in new_watchings:
                CursorHandler.add_watcher(watcher=cursor, watching=other_cursor)

            # 새로운 커서들 전달
            await publish_new_cursors_event(
                target_cursors=[cursor],
                cursors=new_watchings
            )

        # 새로운 위치를 바라보고 있는 커서들 찾기, 본인 제외
        watchers_new_pos = CursorHandler.view_includes(new_position, cursor.conn_id)

        original_watcher_ids = CursorHandler.get_watchers(cursor_id=cursor.conn_id)
        original_watchers = [CursorHandler.get_cursor(id) for id in original_watcher_ids]

        if len(original_watchers) > 0:
            # moved 이벤트 전달
            message = Message(
                event="multicast",
                header={
                    "target_conns": original_watcher_ids,
                    "origin_event": MoveEvent.MOVED,
                },
                payload=MovedPayload(
                    origin_position=original_position,
                    new_position=new_position,
                    color=cursor.color,
                )
            )
            await EventBroker.publish(message)

            # 범위 벗어나면 watcher 제거
            for watcher in original_watchers:
                in_view = watcher.check_in_view(cursor.position)
                if not in_view:
                    CursorHandler.remove_watcher(watcher=watcher, watching=cursor)

        new_watchers = list(filter(lambda c: c.conn_id not in original_watcher_ids, watchers_new_pos))
        if len(new_watchers) > 0:
            # 새로운 watcher 커서들 연관관계 설정
            for other_cursor in new_watchers:
                CursorHandler.add_watcher(watcher=other_cursor, watching=cursor)

            # 새로운 커서들에게 본인 커서 전달
            await publish_new_cursors_event(
                target_cursors=new_watchers,
                cursors=[cursor]
            )

    @EventBroker.add_receiver(InteractionEvent.TILE_STATE_CHANGED)
    @staticmethod
    async def receive_tile_state_changed(message: Message[TileStateChangedPayload]):
        position = message.payload.position
        tile = message.payload.tile

        pub_tile = tile
        if not tile.is_open:
            # 닫힌 타일의 mine, number 정보는 버리기
            pub_tile = tile.copy(hide_info=True)

        # 변경된 타일을 보고있는 커서들에게 전달
        view_cursors = CursorHandler.view_includes(position)
        if len(view_cursors) > 0:
            pub_message = Message(
                event="multicast",
                header={"target_conns": [c.conn_id for c in view_cursors],
                        "origin_event": InteractionEvent.TILE_UPDATED},
                payload=TileUpdatedPayload(
                    position=position,
                    tile=pub_tile
                )
            )
            await EventBroker.publish(pub_message)

        if not (tile.is_open and tile.is_mine):
            return

        # 주변 8칸 커서들 죽이기
        start_p = Point(position.x - 1, position.y + 1)
        end_p = Point(position.x + 1, position.y - 1)

        nearby_cursors = CursorHandler.exists_range(start_p, end_p)
        if len(nearby_cursors) > 0:
            revive_at = datetime.now() + timedelta(minutes=3)

            for c in nearby_cursors:
                c.revive_at = revive_at

            pub_message = Message(
                event="multicast",
                header={"target_conns": [c.conn_id for c in nearby_cursors],
                        "origin_event": InteractionEvent.YOU_DIED},
                payload=YouDiedPayload(
                    revive_at=revive_at
                )
            )
            await EventBroker.publish(pub_message)

    @EventBroker.add_receiver(NewConnEvent.CONN_CLOSED)
    @staticmethod
    async def receive_conn_closed(message: Message[ConnClosedPayload]):
        sender = message.header["sender"]

        cursor = CursorHandler.get_cursor(sender)

        watching = CursorHandler.get_watching(cursor_id=cursor.conn_id)
        watchers = CursorHandler.get_watchers(cursor_id=cursor.conn_id)

        for id in watching:
            other_cursor = CursorHandler.get_cursor(id)
            CursorHandler.remove_watcher(watcher=cursor, watching=other_cursor)

        for id in watchers:
            other_cursor = CursorHandler.get_cursor(id)
            CursorHandler.remove_watcher(watcher=other_cursor, watching=cursor)

        CursorHandler.remove_cursor(cursor.conn_id)

        message = Message(
            event="multicast",
            header={"target_conns": watchers,
                    "origin_event": NewConnEvent.CURSOR_QUIT},
            payload=CursorQuitPayload(
                position=cursor.position,
                pointer=cursor.pointer,
                color=cursor.color
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
