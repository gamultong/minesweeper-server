from event import EventBroker
from board import Board, Point
from message import Message
from message.payload import FetchTilesPayload, TilesPayload, TilesEvent, NewConnEvent, NewConnPayload, TryPointingPayload, PointingResultPayload, PointEvent, MoveEvent, CheckMovablePayload, MovableResultPayload


class BoardHandler():
    @EventBroker.add_receiver(TilesEvent.FETCH_TILES)
    @staticmethod
    async def receive_fetch_tiles(message: Message[FetchTilesPayload]):
        sender = message.header["sender"]

        tiles = Board.fetch(message.payload.start_p, message.payload.end_p)

        resp_message = Message(
            event="multicast",
            header={"target_conns": [sender],
                    "origin_event": TilesEvent.TILES},
            payload=TilesPayload(
                start_p=Point(message.payload.start_p.x,
                              message.payload.start_p.y),
                end_p=Point(message.payload.end_p.x,
                            message.payload.end_p.y),
                tiles=tiles
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

        tiles = Board.fetch(start_p, end_p)

        # TODO: header 추가하기. 위 메서드도
        resp_message = Message(
            event="multicast",
            header={"target_conns": [sender],
                    "origin_event": TilesEvent.TILES},
            payload=TilesPayload(
                start_p=Point(start_p.x, start_p.y),
                end_p=Point(end_p.x, end_p.y),
                tiles=tiles
            )
        )

        await EventBroker.publish(resp_message)

    @EventBroker.add_receiver(PointEvent.TRY_POINTING)
    @staticmethod
    async def receive_try_pointing(message: Message[TryPointingPayload]):
        pointer_x = message.payload.new_pointer.x
        pointer_y = message.payload.new_pointer.y

        if "sender" not in message.header:
            raise "header 없음"

        sender = message.header["sender"]

        tiles = Board.fetch(
            Point(pointer_x-1, pointer_y+1),
            Point(pointer_x+1, pointer_y-1)
        )
        # TODO: TileState에 대한 enum이 생기면 그걸로 변경
        pointable = tiles.find("O") != -1

        await EventBroker.publish(
            Message(
                event=PointEvent.POINTING_RESULT,
                header={"receiver": sender},
                payload=PointingResultPayload(
                    pointable=pointable
                )
            )
        )

    @EventBroker.add_receiver(MoveEvent.CHECK_MOVABLE)
    @staticmethod
    async def receive_check_movable(message: Message[CheckMovablePayload]):
        sender = message.header["sender"]

        position = message.payload.position

        tile = Board.fetch(start=position, end=position)[0]

        # TODO: TileState에 대한 enum이 생기면 그걸로 변경
        movable = tile == "O"

        await EventBroker.publish(
            Message(
                event=MoveEvent.MOVABLE_RESULT,
                header={"receiver": sender},
                payload=MovableResultPayload(
                    position=position,
                    movable=movable
                )
            )
        )
