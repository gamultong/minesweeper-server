from .point import Point
from .tile import Tile
from .tiles import Tiles
from .exceptions import InvalidDataLengthException
from random import randint
from typing import Callable


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
            raise InvalidDataLengthException(expected=expected_len, actual=len(data.data))

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
        return Section(p, bytearray.fromhex(data))

    @staticmethod
    def create(p: Point):
        total = Section.LENGTH**2
        mine_cnt = int((total * Section.MINE_RATIO)//1)

        mine = 0b01000000
        num_mask = 0b00000111

        # zero-value로 초기화됨,
        data = bytearray(total)

        for _ in range(mine_cnt):
            # 랜덤 위치가 잘못된 경우 재시도
            while True:
                rand_p = Point(
                    x=randint(0, Section.LENGTH - 1),
                    y=randint(0, Section.LENGTH - 1)
                )

                rand_idx = (rand_p.y * Section.LENGTH) + rand_p.x
                cur_tile = data[rand_idx]

                # 이미 지뢰가 존재
                if cur_tile == mine:
                    continue

                # 주변 타일 검사
                invalid = False

                def check_neighbor_restrictions(t: int) -> tuple[Tile | None, bool]:
                    nonlocal invalid
                    # 주변 타일이 7을 넘지 않아야 함
                    if t & num_mask == 7:
                        invalid = True

                    return None, invalid

                for_each_neighbor(tiles=data, p=rand_p, func=check_neighbor_restrictions)
                if invalid:
                    continue

                data[rand_idx] = mine

                # 주변 타일 숫자 증가
                def increase_number(t: int) -> tuple[Tile | None, bool]:
                    if t == mine:
                        return None, False

                    t += 1

                    return t, False

                for_each_neighbor(tiles=data, p=rand_p, func=increase_number)

                break

        return Section(p=p, data=data)


# (x, y)
_delta = [
    (0, 1), (0, -1), (-1, 0), (1, 0),  # 상하좌우
    (-1, 1), (1, 1), (-1, -1), (1, -1),  # 좌상 우상 좌하 우하
]


def for_each_neighbor(tiles: bytearray, p: Point, func: Callable[[int], tuple[int | None, bool]]):
    """
    p(section 내부 좌표)의 주변 8방향의 인접 타일을 돌며 func를 실행.
    만약 인접 타일이 section의 범위를 벗어난다면 무시함.

    [func 반환값]
    tile: None이 아니면 타일을 업데이트.
    stop: True면 반복 중지
    """

    # 주변 탐색
    for dx, dy in _delta:
        np = Point(p.x+dx, p.y+dy)
        if \
                np.x < 0 or np.x >= Section.LENGTH or \
                np.y < 0 or np.y >= Section.LENGTH:
            continue

        new_idx = (np.y * Section.LENGTH) + np.x
        nearby_tile = tiles[new_idx]

        tile, stop = func(nearby_tile)
        if tile is not None:
            tiles[new_idx] = tile

        if stop:
            break


if __name__ == "__main__":
    sec = Section.create(Point(0, 0))
    for i in range(100):
        print("".join(map(lambda x: "m" if x == 0b01000000 else "c", sec.data[i*100:(i+1)*100])))
    print(sec.data.count(0b01000000))
    print(sec.data.count(0b00000000))
