from dataclasses import dataclass

from face import Face
from render_type import RenderType

@dataclass
class TexturedTriangle:
    type: RenderType
    z_center: float
    face: Face