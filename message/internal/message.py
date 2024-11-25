from typing import Generic, TypeVar
from message.payload import Payload, FetchTilesPayload, TilesPayload
from .exceptions import InvalidEventTypeException

import json

EVENT_TYPE = TypeVar(
    "EVENT_TYPE",
    bound=Payload
)

PAYLOAD_DICT: dict[str, Payload] = {
    "fetch-tiles": FetchTilesPayload,
    "tiles": TilesPayload
}


class Message(Generic[EVENT_TYPE]):
    def __init__(self, event: str, payload: EVENT_TYPE, header: dict[str, object] = {}):
        self.event = event
        self.header = header
        self.payload = payload

    def to_str(self, del_header: bool = True):
        data = self
        if del_header:
            data = Message(event=self.event, payload=self.payload)
            del data.header

        return json.dumps(
            data,
            default=lambda o: o.__dict__,
            sort_keys=True
        )

    @staticmethod
    def from_str(msg: str):
        decoded = json.loads(msg)

        event = decoded["event"]
        payload = decode_data(event, decoded["payload"])

        message = Message(event=event, payload=payload)
        if "header" in decoded:
            message.header = decoded["header"]

        return message


def decode_data(event: str, data: dict):
    """
    data를 Payload로 decode
    """
    if not event in PAYLOAD_DICT:
        raise InvalidEventTypeException(event)

    return PAYLOAD_DICT[event]._from_dict(data)
