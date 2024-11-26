from board import Point
from .color import Color
from dataclasses import dataclass


@dataclass
class Cursor:
    conn_id: str
    position: Point
    pointer: Point | None
    color: Color
    width: int
    height: int

    @staticmethod
    def create(conn_id: str):
        return Cursor(
            conn_id=conn_id,
            position=Point(0, 0),
            pointer=None,
            color=Color.get_random(),
            width=0,
            height=0
        )

    def set_size(self, width: int, height: int):
        self.width = width
        self.height = height
