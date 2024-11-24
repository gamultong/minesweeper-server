from fastapi.testclient import TestClient
from server import app
from message import Message
from message.payload import FetchTilesPayload, TilesPayload, TilesEvent
from board.test.fixtures import setup_board

client = TestClient(app)


def test_fetch_tiles():
    setup_board()

    with client.websocket_connect("/session") as websocket:
        msg = Message(
            event=TilesEvent.FETCH_TILES,
            payload=FetchTilesPayload(
                start_x=-2,
                start_y=1,
                end_x=1,
                end_y=-2
            )
        )
        expect = Message(
            event=TilesEvent.TILES,
            payload=TilesPayload(
                start_x=-2,
                start_y=1,
                end_x=1,
                end_y=-2,
                tiles="df12df12er56er56"
            )
        )

        websocket.send_text(msg.to_str())

        response = websocket.receive_text()

        assert response == expect.to_str()


test_fetch_tiles()
