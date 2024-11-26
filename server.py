from fastapi import FastAPI, WebSocket, Response
from conn.manager import ConnectionManager
from board.handler import BoardHandler

app = FastAPI()


@app.websocket("/session")
async def session(ws: WebSocket):
    try:
        view_width = int(ws.headers["X-View-Tiles-Width"])
        view_height = int(ws.headers["X-View-Tiles-Height"])
    except KeyError:
        await ws.close(code=400, reason="Missing required headers")
        return
    except ValueError:
        await ws.close(code=400, reason="Headers are not properly typed")
        return

    conn = await ConnectionManager.add(ws, width=view_width, height=view_height)

    while True:
        try:
            msg = await conn.receive()
            await ConnectionManager.handle_message(msg, conn.id)
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
