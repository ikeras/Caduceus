from dataclasses import dataclass
from typing import List

from pcx import Pcx
from point2d import Point2d

@dataclass
class Face:
    triangle_verts: List[Point2d]
    skin_verts: List[Point2d]
    texture: Pcx