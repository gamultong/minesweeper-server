from fastapi import FastAPI, WebSocket, Response
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

    await ConnectionManager.close(conn)

@app.get("/")
def health_check():
    return Response()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)