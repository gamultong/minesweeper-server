from enum import Enum
from dataclasses import dataclass

class TileState(Enum):
    OPEN = ord('O')
    CLOSED = ord('C')
    MINE = ord('M')

@dataclass
class Point:
    x: int
    y: int

SECTION_LENGTH = 100

class Section:
    def __init__(self, p:Point, data):
        self.p = p
        self.data = data


    def __getitem__(self, *args):
        slc:slice|int = args[0]
        if type(slc) == int:
            return self.data[slc]
        
        start_y = slc.start if slc.start else 0
        end_y = slc.stop if slc.stop else SECTION_LENGTH

        class wrapper:
            def __getitem__(wp_self, *args):
                wp_slc:slice|int = args[0]
                if type(wp_slc) == int:
                    wp_slc = slice(wp_slc, wp_slc+1, None)

                start_x = wp_slc.start if wp_slc.start else 0
                end_x = wp_slc.stop if wp_slc.stop else SECTION_LENGTH
                
                result = [self.data[i][start_x:end_x] for i in range(start_y, end_y)]

                return result
            
            def __setitem__(wp_self, *args):
                wp_slc:slice|int = args[0]
                wp_data = args[1]
                if type(wp_slc) == int:
                    wp_slc = slice(wp_slc, wp_slc+1, None)

                start_x = wp_slc.start if wp_slc.start else 0
                end_x = wp_slc.stop if wp_slc.stop else SECTION_LENGTH
                for y in range(start_y, end_y):
                    self.data[y] = self.data[y][:start_x] + wp_data[y-start_y] + self.data[y][end_x:]
                return 
        
        return wrapper()

    def __setitem__(self, *args):
        slc:slice|int = args[0]
        data = args[1]
        if type(slc) == int:
            if type(data) != bytearray:
                raise
            if len(data) != SECTION_LENGTH:
                raise
            self.data[slc] = data
            return
        return 
    
    def fetch(self, start:Point, end:Point|None = None) -> list[bytearray]|bytes:
        if end:
            return self[start.y:end.y+1][start.x:end.x+1]
        else:
            return bytes([self[start.y][start.x]])
    
    def update(self, data, start:Point, end:Point|None = None) -> None:
        if end:
            self[start.y:end.y+1][start.x:end.x+1] = data
        else:
            self[start.y][start.x] = data[0]
        return
        

    @staticmethod
    def from_str(p:Point, data):
        arr = [bytearray(data[i*SECTION_LENGTH:(i*SECTION_LENGTH)+SECTION_LENGTH], "ascii") for i in range(SECTION_LENGTH)]
        return Section(p, arr)
    

