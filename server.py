from fastapi import FastAPI, WebSocket, Response
from conn.manager import ConnectionManager
from board.event.handler import BoardEventHandler

app = FastAPI()


@app.websocket("/session")
async def session(ws: WebSocket):
    try:
        view_width = int(ws.query_params["view_wdith"])
        view_height = int(ws.query_params["view_height"])
    except KeyError:
        await ws.close(code=400, reason="Missing required data")
        return
    except ValueError:
        await ws.close(code=400, reason="Data not properly typed")
        return

    conn = await ConnectionManager.add(ws, width=view_width, height=view_height)

    while True:
        try:
            msg = await conn.receive()
            msg.header = {"sender": conn.id}
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
