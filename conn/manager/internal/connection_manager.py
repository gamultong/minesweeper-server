from fastapi.websockets import WebSocket
from conn import Conn
from message import Message
from message.payload import TilesPayload, NewConnEvent, NewConnPayload
from event import EventBroker
from uuid import uuid4


class ConnectionManager:
    conns: dict[str, Conn] = {}

    @staticmethod
    def get_conn(id: str):
        if id in ConnectionManager.conns:
            return ConnectionManager.conns[id]
        return None

    @staticmethod
    async def add(conn: WebSocket, width: int, height: int) -> Conn:
        id = ConnectionManager.generate_conn_id()

        conn_obj = Conn(id=id, conn=conn)
        await conn_obj.accept()
        ConnectionManager.conns[id] = conn_obj

        message = Message(
            event=NewConnEvent.NEW_CONN,
            payload=NewConnPayload(
                conn_id=id,
                height=height,
                width=width
            )
        )

        await EventBroker.publish(message)

        return conn_obj

    @staticmethod
    async def close(conn: Conn) -> Conn:
        ConnectionManager.conns.pop(conn.id)

    @staticmethod
    def generate_conn_id():
        while (id := uuid4().hex) in ConnectionManager.conns:
            pass
        return id

    @EventBroker.add_receiver("tiles")
    @staticmethod
    async def receive_tiles_event(message: Message[TilesPayload]):
        for id in ConnectionManager.conns:
            conn = ConnectionManager.conns[id]
            await conn.send(message)

    @staticmethod
    async def handle_message(message: Message, conn_id: str):
        message.header["sender"] = conn_id
        await EventBroker.publish(message)
