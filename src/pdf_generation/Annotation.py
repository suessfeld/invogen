import time


class Position:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)


class DataObject:
    type: str
    value: str
    position: Position


class Annotation:
    meta: dict
    data: dict[DataObject]

    def __init__(self):
        self.meta = {'timestamp': time.time(), 'version': '0.01', 'image_size': 'implement me!'}
        self.data = {}
