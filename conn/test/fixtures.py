from unittest.mock import MagicMock, AsyncMock

from fastapi.websockets import WebSocket


def create_connection_mock() -> WebSocket:
    con = MagicMock()
    con.accept = AsyncMock()
    con.receive_text = AsyncMock()
    con.send_text = AsyncMock()
    con.close = AsyncMock()

    return con
