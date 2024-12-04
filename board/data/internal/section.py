from .point import Point
from .tiles import Tiles
from random import randint


class Section:
    LENGTH = 100
    MINE_RATIO = 0.3

    def __init__(self, p: Point, data: bytearray):
        self.p = p
        self.data = data

    def fetch(self, start: Point, end: Point | None = None) -> Tiles:
        if end is None:
            end = start

        # row 당 가져올 원소 개수 + 1
        x_gap = end.x - start.x + 1

        result = bytearray()
        for y in range(start.y, end.y-1, -1):
            # (row 길이 * y의 실제 인덱스 위치) + x 오프셋
            idx_start = Section.LENGTH * (Section.LENGTH - y - 1) + start.x
            result += self.data[idx_start: idx_start+x_gap]

        return Tiles(data=result)

    def update(self, data: Tiles, start: Point, end: Point | None = None) -> None:
        if end is None:
            end = start

        expected_len = (end.x - start.x + 1) * (start.y - end.y + 1)
        if len(data.data) != expected_len:
            raise "예상 길이와 다름"

        x_gap = end.x - start.x + 1

        for y in range(start.y, end.y-1, -1):
            idx_start = Section.LENGTH * (Section.LENGTH - y - 1) + start.x
            offset = (start.y - y) * x_gap
            self.data[idx_start: idx_start+x_gap] = data.data[offset: offset+x_gap]

    @property
    def abs_x(self):
        return self.p.x * Section.LENGTH

    @property
    def abs_y(self):
        return self.p.y * Section.LENGTH

    @staticmethod
    def from_str(p: Point, data: str):
        """
        레거시, 관련 로직 바꿔야 함.
        """
        return Section(p, bytearray(data, encoding="ascii"))

    @staticmethod
    def create(p: Point):
        total = Section.LENGTH**2
        tiles = int((total * (1-Section.MINE_RATIO))//1)
        mine = total - tiles

        def rand_choice():
            nonlocal mine
            nonlocal tiles
            r = randint(1, tiles+mine)
            q = tiles >= r
            if q:
                tiles -= 1
            else:
                mine -= 1
            return q
        # TODO: number도 저장하기
        data = bytearray(
            0b00000000
            if rand_choice()
            else 0b01000000
            for _ in range(total)
        )

        return Section(p=p, data=data)


if __name__ == "__main__":
    sec = Section.create(Point(0, 0))
    for i in range(100):
        print("".join(map(lambda x: "m" if x == 0b01000000 else "c", sec.data[i*100:(i+1)*100])))
    print(sec.data.count(0b01000000))
    print(sec.data.count(0b00000000))
