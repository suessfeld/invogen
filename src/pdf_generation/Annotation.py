import time
import datetime


class Position:
    x1: int
    y1: int
    x2: int
    y2: int

    def __init__(self, x1, y1, x2, y2):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)


class DataObject:
    type: str
    value: str
    position: Position


class Annotation:
    meta: dict
    data: dict[DataObject]

    def __init__(self):
        self.meta = {'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'version': '0.01',
                     'image_size': 'implement me!'}
        self.data = {}
