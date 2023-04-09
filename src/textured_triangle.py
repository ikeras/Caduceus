from dataclasses import dataclass

from face import Face

@dataclass
class TexturedTriangle:
    z_center: float
    face: Face