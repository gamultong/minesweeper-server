from fastapi.websockets import WebSocket
from conn import Conn
from message import Message
from message.payload import TilesPayload, NewConnEvent, NewConnPayload
from event import EventBroker
from uuid import uuid4


def overwrite_event(msg: Message):
    if "origin_event" not in msg.header:
        return

    msg.event = msg.header["origin_event"]
    del msg.header["origin_event"]


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

    @EventBroker.add_receiver("broadcast")
    @staticmethod
    async def receive_broadcast_event(message: Message):
        overwrite_event(message)
        for id in ConnectionManager.conns:
            conn = ConnectionManager.conns[id]
            await conn.send(message)

    @EventBroker.add_receiver("multicast")
    @staticmethod
    async def receive_multicast_event(message: Message):
        overwrite_event(message)
        if "target_conns" not in message.header:
            raise "header에 target_conns 없음"
        for conn_id in message.header["target_conns"]:
            conn = ConnectionManager.get_conn(conn_id)
            if not conn:
                raise "connection 없음"

            await conn.send(message)

    @staticmethod
    async def handle_message(message: Message):
        await EventBroker.publish(message)
