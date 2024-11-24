from fastapi.websockets import WebSocket
from message import Message
from dataclasses import dataclass


@dataclass
class Conn:
    id: str
    conn: WebSocket

    @staticmethod
    def create(id: str, ws: WebSocket):
        return Conn(id=id, conn=ws)

    async def accept(self):
        await self.conn.accept()

    async def close(self):
        await self.conn.close()

    async def receive(self):
        return Message.from_str(await self.conn.receive_text())

    async def send(self, msg: Message):
        await self.conn.send_text(msg.to_str())
