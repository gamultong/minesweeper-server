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

    def set_size(self, width: int, height: int):
        self.width = width
        self.height = height

    def check_in_view(self, p: Point):
        leftmost = self.position.x - self.width
        rightmost = self.position.x + self.width
        top = self.position.y + self.height
        bottom = self.position.y - self.height

        return \
            p.x >= leftmost and p.x <= rightmost and \
            p.y >= bottom and p.y <= top

    def check_interactable(self, p: Point):
        return \
            p.x >= self.position.x - 1 and \
            p.x <= self.position.x + 1 and \
            p.y >= self.position.y - 1 and \
            p.y <= self.position.y + 1

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
