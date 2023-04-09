import os
from typing import Generator

from model import QuakeModel
from render_type import RenderType
from textured_triangle import TexturedTriangle

class Character:
    def __init__(self, render_type: RenderType, quake_filename: str, weapon_filename: str):
        character_pcx_filename = Character._get_pcx_filename(quake_filename)
        weapon_pcx_filename = Character._get_pcx_filename(weapon_filename)

        self._model = QuakeModel(render_type)
        self._model.from_file(quake_filename, character_pcx_filename)
        
        self._weapon = QuakeModel(render_type)
        self._weapon.from_file(weapon_filename, weapon_pcx_filename)
        
        self.rotate(0, 180, 90)
        self.translate(85, -250, 70)
        self.scale(1)

    @property
    def render_type(self) -> RenderType:
        return self._model.render_type

    @render_type.setter
    def render_type(self, render_type: RenderType) -> None:
        self._model.render_type = render_type
        self._weapon.render_type = render_type

    @property
    def rotate_x(self) -> int:
        return self._rotate_x

    @property
    def rotate_y(self) -> int:
        return self._rotate_y

    @property
    def rotate_z(self) -> int:
        return self._rotate_z
    
    @property
    def size(self) -> float:
        return self._size
        
    @property
    def sequence_name(self) -> str:
        return self._model.sequence_name
     
    def advance_frame(self) -> None:
        self._model.advance_frame()
        self._weapon.advance_frame()
    
    def advance_sequence(self) -> None:
        self._model.advance_sequence()
        self._weapon.advance_sequence()
        
    def previous_sequence(self) -> None:
        self._model.previous_sequence()
        self._weapon.previous_sequence()        
            
    def rotate(self, angle_x: int, angle_y: int, angle_z: int) -> None:
        self._rotate_x = angle_x
        self._rotate_y = angle_y
        self._rotate_z = angle_z
        self._model.rotate(angle_x, angle_y, angle_z)
        self._weapon.rotate(angle_x, angle_y, angle_z)
    
    def scale(self, scale: float) -> None:
        self._size = scale
        self._model.scale(scale)
        self._weapon.scale(scale)
        
    def translate(self, x: int, y: int, z: int) -> None:
        self._model.translate(x, y, z)
        self._weapon.translate(x, y, z)
    
    def triangle_in_frame(self) -> Generator[TexturedTriangle, None, None]:
        for triangle in self._model.triangle_in_frame():
            yield triangle
        
        for triangle in self._weapon.triangle_in_frame():
            yield triangle
        
    @staticmethod
    def _get_pcx_filename(filename: str) -> str:
        base_name, _ = os.path.splitext(filename)
        pcx_filename = base_name + '.pcx'
        
        if not os.path.exists(pcx_filename):
            raise ValueError(f'Unable to find the texture for this quake model: {pcx_filename}')
                
        return pcx_filename