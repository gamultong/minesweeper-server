from fastapi import FastAPI, WebSocket, Response
from conn.manager import ConnectionManager
from board.event.handler import BoardEventHandler
from cursor.event.handler import CursorEventHandler

app = FastAPI()


@app.websocket("/session")
async def session(ws: WebSocket):
    try:
        view_width = int(ws.query_params.get("view_width"))
        view_height = int(ws.query_params.get("view_height"))
    except KeyError as e:
        print(f"WebSocket connection closed: {e}")
        await ws.close(code=1000, reason="Missing required data")
        return
    except TypeError as e:
        print(f"WebSocket connection closed: {e}")
        await ws.close(code=1000, reason="Data not properly typed")
        return
    except Exception as e:
        await ws.close(code=1006, reason=e.__repr__())
        return

    conn = await ConnectionManager.add(ws, width=view_width, height=view_height)

    while True:
        try:
            msg = await conn.receive()
            msg.header = {"sender": conn.id}
            await ConnectionManager.handle_message(msg)
        except Exception as e:
            msg = e
            if hasattr(e, "msg"):
                msg = e.msg
            print(f"WebSocket connection closed: {type(e)} '{msg}'")
            break

    await ConnectionManager.close(conn)


@app.get("/")
def health_check():
    return Response()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
