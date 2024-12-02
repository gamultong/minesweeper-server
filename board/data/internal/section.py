from .point import Point


class Section:
    LENGTH = 100

    def __init__(self, p: Point, data):
        self.p = p
        self.data = data

    def __getitem__(self, *args):
        slc: slice | int = args[0]
        if type(slc) == int:
            return self.data[slc]

        start_y = slc.start if slc.start != None else 0
        end_y = slc.stop if slc.stop != None else Section.LENGTH

        start_y = to_inner_index(start_y)
        end_y = to_inner_index(end_y)

        class wrapper:
            def __getitem__(wp_self, *args):
                wp_slc: slice | int = args[0]
                if type(wp_slc) == int:
                    wp_slc = slice(wp_slc, wp_slc+1, None)

                start_x = wp_slc.start if wp_slc.start else 0
                end_x = wp_slc.stop if wp_slc.stop else Section.LENGTH

                result = [self.data[i][start_x:end_x] for i in range(start_y, end_y+1)]

                return result

            def __setitem__(wp_self, *args):
                wp_slc: slice | int = args[0]
                wp_data = args[1]
                if type(wp_slc) == int:
                    wp_slc = slice(wp_slc, wp_slc+1, None)

                start_x = wp_slc.start if wp_slc.start else 0
                end_x = wp_slc.stop if wp_slc.stop else Section.LENGTH
                for y in range(start_y, end_y+1):
                    self.data[y] = self.data[y][:start_x] + wp_data[y-start_y] + self.data[y][end_x:]
                return

        return wrapper()

    def __setitem__(self, *args):
        slc: slice | int = args[0]
        data = args[1]
        if type(slc) == int:
            if type(data) != bytearray:
                raise
            if len(data) != Section.LENGTH:
                raise
            self.data[slc] = data
            return
        return

    def fetch(self, start: Point, end: Point | None = None) -> list[bytearray] | bytes:
        if end:
            data = self[start.y:end.y][start.x:end.x+1]
        else:
            data = bytes([self[start.y][start.x]])
        return data

    def update(self, data, start: Point, end: Point | None = None) -> None:
        if end:
            self[start.y:end.y][start.x:end.x+1] = data
        else:
            self[start.y][start.x] = data[0]

    def _debug(self):
        print("---------------------------------")
        print("section lenght  :", Section.LENGTH)
        print("section point x :", self.abs_x)
        print("              y :", self.abs_y)
        print("section data    :")
        print("---------------------------------")
        for i in range(Section.LENGTH):
            print(self.data[i])
        print("---------------------------------")

    @property
    def abs_x(self):
        return self.p.x * Section.LENGTH

    @property
    def abs_y(self):
        return self.p.y * Section.LENGTH

    @staticmethod
    def from_str(p: Point, data):
        arr = [bytearray(data[i*Section.LENGTH:(i*Section.LENGTH)+Section.LENGTH], "ascii") for i in range(Section.LENGTH)]
        return Section(p, arr)


def to_inner_index(y):
    return Section.LENGTH - 1 - y
