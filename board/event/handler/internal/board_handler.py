from event import EventBroker
from board.data import Point, Tile
from board.data.handler import BoardHandler
from cursor.data import Color
from message import Message
from message.payload import (
    FetchTilesPayload,
    TilesPayload,
    TilesEvent,
    NewConnEvent,
    NewConnPayload,
    TryPointingPayload,
    PointingResultPayload,
    PointEvent,
    MoveEvent,
    CheckMovablePayload,
    MovableResultPayload,
    ClickType,
    InteractionEvent,
    TileStateChangedPayload
)


class BoardEventHandler():
    @EventBroker.add_receiver(TilesEvent.FETCH_TILES)
    @staticmethod
    async def receive_fetch_tiles(message: Message[FetchTilesPayload]):
        sender = message.header["sender"]

        await BoardEventHandler._publish_tiles(message.payload.start_p, message.payload.end_p, [sender])

    @EventBroker.add_receiver(NewConnEvent.NEW_CONN)
    @staticmethod
    async def receive_new_conn(message: Message[NewConnPayload]):
        sender = message.header["sender"]

        # 0, 0 기준으로 fetch
        width = message.payload.width
        height = message.payload.height

        start_p = Point(x=-width, y=height)
        end_p = Point(x=width, y=-height)

        await BoardEventHandler._publish_tiles(start_p, end_p, [sender])

    @staticmethod
    async def _publish_tiles(start: Point, end: Point, to: list[str]):
        tiles = BoardHandler.fetch(start, end)
        tiles.hide_info()

        pub_message = Message(
            event="multicast",
            header={"target_conns": to,
                    "origin_event": TilesEvent.TILES},
            payload=TilesPayload(
                start_p=Point(start.x, start.y),
                end_p=Point(end.x, end.y),
                tiles=tiles.to_str()
            )
        )

        await EventBroker.publish(pub_message)

    @EventBroker.add_receiver(PointEvent.TRY_POINTING)
    @staticmethod
    async def receive_try_pointing(message: Message[TryPointingPayload]):
        pointer = message.payload.new_pointer

        if "sender" not in message.header:
            raise "header 없음"

        sender = message.header["sender"]

        tiles = BoardHandler.fetch(
            Point(pointer.x-1, pointer.y+1),
            Point(pointer.x+1, pointer.y-1)
        )

        pointable = False
        for tile in tiles.data:
            t = Tile.from_int(tile)
            if t.is_open:
                pointable = True
                break

        pub_message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": sender},
            payload=PointingResultPayload(
                pointer=pointer,
                pointable=pointable
            )
        )

        await EventBroker.publish(pub_message)

        if not pointable:
            return

        # 보드 상태 업데이트하기
        tile = Tile.from_int(tiles.data[4])  # 3x3칸 중 가운데
        click_type = message.payload.click_type

        if tile.is_open:
            return

        match (click_type):
            # 닫힌 타일 열기
            case ClickType.GENERAL_CLICK:
                if tile.is_flag:
                    return

                tile.is_open = True

            # 깃발 꽂기/뽑기
            case ClickType.SPECIAL_CLICK:
                color = message.payload.color

                tile.is_flag = not tile.is_flag
                tile.color = color if tile.is_flag else None

        BoardHandler.update_tile(pointer, tile)

        pub_message = Message(
            event=InteractionEvent.TILE_STATE_CHANGED,
            payload=TileStateChangedPayload(
                position=pointer,
                tile=tile
            )
        )

        await EventBroker.publish(pub_message)

    @EventBroker.add_receiver(MoveEvent.CHECK_MOVABLE)
    @staticmethod
    async def receive_check_movable(message: Message[CheckMovablePayload]):
        sender = message.header["sender"]

        position = message.payload.position

        tiles = BoardHandler.fetch(start=position, end=position)
        tile = Tile.from_int(tiles.data[0])

        movable = tile.is_open

        message = Message(
            event=MoveEvent.MOVABLE_RESULT,
            header={"receiver": sender},
            payload=MovableResultPayload(
                position=position,
                movable=movable
            )
        )

        await EventBroker.publish(message)
