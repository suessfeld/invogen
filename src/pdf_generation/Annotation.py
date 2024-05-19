
class AnnotationValue:
    x: float
    y: float
    width: float
    height: float
    rotation: int
    rectanglelabels: []

class AnnotationResult:
    id: str
    type: str
    value: AnnotationValue
    to_name: str
    from_name: str
    image_rotation: int
    original_width: int
    original_height: int

class AnnotationObject:
    result: []
    ground_truth: bool

class Annotation:
    data: dict
    annotations: []

    def __init__(self):
        self.annotations = []
        self.data = {}
