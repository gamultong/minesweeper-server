from dataclasses import dataclass


@dataclass
class Tiles:
    data: list[bytearray]

    def to_str(self):
        return bytearray().join(self.data).decode("ascii")
