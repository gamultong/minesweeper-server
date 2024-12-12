class InvalidTileException(Exception):
    msg: str = "invalid tile"


class InvalidDataLengthException(Exception):
    def __init__(self, expected: int, actual: int):
        self.msg = f"invalid data length. expected: {expected}, actual: {actual}"
