from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int

    def copy(self):
        return Point(self.x, self.y)
