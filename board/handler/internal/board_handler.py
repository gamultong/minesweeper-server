from event import EventBroker
from board import Board
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
                start_x=message.payload.start_x,
                start_y=message.payload.start_y,
                end_x=message.payload.end_x,
                end_y=message.payload.end_y,
                tiles=tiles
            )
        )

        await EventBroker.publish(resp_message)