"""
Represents the attributes for a single generation job.
"""
class GenerationAttributes:
    amount: int
    seed: str
    output_path: str


class BoundingBox:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
