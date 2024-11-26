from event import EventBroker
from board import Board, Point
from message import Message
from message.payload import FetchTilesPayload, TilesPayload, TilesEvent


class BoardHandler():
    @EventBroker.add_receiver(TilesEvent.FETCH_TILES)
    @staticmethod
    async def receive_fetch_tiles_event(message: Message[FetchTilesPayload]):
        tiles = Board.fetch(message.payload.start_p, message.payload.end_p)

        resp_message = Message(
            event=TilesEvent.TILES,
            payload=TilesPayload(
                start_p=Point(message.payload.start_p.x,
                    message.payload.start_p.y),
                end_p=Point(message.payload.end_p.x,
                    message.payload.end_p.y),
                tiles=tiles
            )
        )

        await EventBroker.publish(resp_message)
