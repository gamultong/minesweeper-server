from unittest.mock import MagicMock, AsyncMock

from fastapi.websockets import WebSocket


class ConnMock():
    def __init__(self):
        self.accept = AsyncMock()
        self.receive_text = AsyncMock()
        self.send_text = AsyncMock()
        self.close = AsyncMock()


def create_connection_mock() -> ConnMock:
    return ConnMock()
