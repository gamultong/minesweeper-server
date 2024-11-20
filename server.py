from fastapi import FastAPI, WebSocket
from conn.manager import ConnectionManager
from board.handler import BoardHandler

app = FastAPI()

@app.websocket("/session")
async def session(ws: WebSocket):
    conn = await ConnectionManager.add(ws)
    
    while True:
        try:
            msg = await conn.receive()
            await ConnectionManager.handle_message(msg)
        except Exception as e:
            print(f"WebSocket connection closed: {e}")
            break
