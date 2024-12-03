from event import EventBroker
from board.data import Point
from board.data.handler import BoardHandler
from message import Message
from message.payload import FetchTilesPayload, TilesPayload, TilesEvent, NewConnEvent, NewConnPayload, TryPointingPayload, PointingResultPayload, PointEvent, MoveEvent, CheckMovablePayload, MovableResultPayload


class BoardEventHandler():
    @EventBroker.add_receiver(TilesEvent.FETCH_TILES)
    @staticmethod
    async def receive_fetch_tiles(message: Message[FetchTilesPayload]):
        sender = message.header["sender"]

        tiles = BoardHandler.fetch(message.payload.start_p, message.payload.end_p)
        tiles_str = tiles.to_str()

        resp_message = Message(
            event="multicast",
            header={"target_conns": [sender],
                    "origin_event": TilesEvent.TILES},
            payload=TilesPayload(
                start_p=Point(message.payload.start_p.x,
                              message.payload.start_p.y),
                end_p=Point(message.payload.end_p.x,
                            message.payload.end_p.y),
                tiles=tiles_str
            )
        )

        await EventBroker.publish(resp_message)

    @EventBroker.add_receiver(NewConnEvent.NEW_CONN)
    @staticmethod
    async def receive_new_conn(message: Message[NewConnPayload]):
        sender = message.header["sender"]

        # 0, 0 기준으로 fetch
        width = message.payload.width
        height = message.payload.height
        start_p = Point(x=-width, y=height)
        end_p = Point(x=width, y=-height)

        tiles = BoardHandler.fetch(start_p, end_p)
        tiles_str = tiles.to_str()

        # TODO: header 추가하기. 위 메서드도
        resp_message = Message(
            event="multicast",
            header={"target_conns": [sender],
                    "origin_event": TilesEvent.TILES},
            payload=TilesPayload(
                start_p=Point(start_p.x, start_p.y),
                end_p=Point(end_p.x, end_p.y),
                tiles=tiles_str
            )
        )

        await EventBroker.publish(resp_message)

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
        tiles_str = tiles.to_str()

        # TODO: TileState에 대한 enum이 생기면 그걸로 변경
        pointable = tiles_str.find("O") != -1

        message = Message(
            event=PointEvent.POINTING_RESULT,
            header={"receiver": sender},
            payload=PointingResultPayload(
                pointer=pointer,
                pointable=pointable
            )
        )

        await EventBroker.publish(message)

    @EventBroker.add_receiver(MoveEvent.CHECK_MOVABLE)
    @staticmethod
    async def receive_check_movable(message: Message[CheckMovablePayload]):
        sender = message.header["sender"]

        position = message.payload.position

        tile = BoardHandler.fetch(start=position, end=position)
        tile = tile.to_str()[0]

        # TODO: TileState에 대한 enum이 생기면 그걸로 변경
        movable = tile == "O"

        message = Message(
            event=MoveEvent.MOVABLE_RESULT,
            header={"receiver": sender},
            payload=MovableResultPayload(
                position=position,
                movable=movable
            )
        )

        await EventBroker.publish(message)
