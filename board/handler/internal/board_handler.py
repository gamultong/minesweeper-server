from event import EventBroker
from board import Board, Point
from message import Message
from message.payload import FetchTilesPayload, TilesPayload, TilesEvent, NewConnEvent, NewConnPayload


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
                start_x=message.payload.start_x,
                start_y=message.payload.start_y,
                end_x=message.payload.end_x,
                end_y=message.payload.end_y,
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
                start_x=start_p.x,
                start_y=start_p.y,
                end_x=end_p.x,
                end_y=end_p.y,
                tiles=tiles
            )
        )

        await EventBroker.publish(resp_message)
