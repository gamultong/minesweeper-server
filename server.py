from fastapi.websockets import WebSocket
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class Conn:
    id: str
    conn: WebSocket

class ConnectionManager:
    conns: dict[str, Conn] = {}

    @staticmethod
    def get_conn(id:str):
        if id in ConnectionManager.conns:
            return ConnectionManager.conns[id]
        return None
    
    @staticmethod
    def add(conn: WebSocket):
        id = ConnectionManager.generate_conn_id()

        conn_obj = Conn(id=id, conn=conn)
        ConnectionManager.conns[id] = conn_obj

        return conn_obj

    @staticmethod
    def generate_conn_id():
        while (id:=uuid4().hex) in ConnectionManager.conns:
            pass
        return id
