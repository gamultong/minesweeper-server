from dataclasses import dataclass


@dataclass
class Tiles:
    data: bytearray

    def to_str(self):
        return self.data.decode("ascii")
