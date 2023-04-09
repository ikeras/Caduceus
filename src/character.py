import os

from model import QuakeModel
from render_type import RenderType

class Character:
    def __init__(self, render_type: RenderType, quake_filename: str, weapon_filename: str):
        character_pcx_filename = Character._get_pcx_filename(quake_filename)
        weapon_pcx_filename = Character._get_pcx_filename(weapon_filename)

        self._model = QuakeModel(RenderType.WIREFRAME)
        self._model.from_file(quake_filename, character_pcx_filename)
        self._model.rotate(0, 180, 90)
        self._model.translate(70, -250, 70)
        self._model.scale(1)
        
        self._weapon = QuakeModel(RenderType.WIREFRAME)
        self._weapon.from_file(weapon_filename, weapon_pcx_filename)
        self._weapon.rotate(0, 180, 90)
        self._weapon.translate(70, -250, 70)
        self._weapon.scale(1)        
    
    def advance_frame(self):
        self._model.advance_frame()
        self._weapon.advance_frame()
        
    @property
    def render_type(self):
        return self._model.render_type

    @render_type.setter
    def render_type(self, render_type: RenderType):
        self._model.render_type = render_type
        self._weapon.render_type = render_type

    def rotate(self, angle_x, angle_y, angle_z):
        self._model.rotate(angle_x, angle_y, angle_z)
        self._weapon.rotate(angle_x, angle_y, angle_z)
        
    def scale(self, scale):
        self._model.scale(scale)
        self._weapon.scale(scale)
        
    def translate(self, x, y, z):
        self._model.translate(x, y, z)
        self._weapon.translate(x, y, z)
    
    def triangle_in_frame(self):
        for triangle in self._model.triangle_in_frame():
            yield triangle
        
        for triangle in self._weapon.triangle_in_frame():
            yield triangle
        
    @staticmethod
    def _get_pcx_filename(filename: str):
        base_name, _ = os.path.splitext(filename)
        pcx_filename = base_name + '.pcx'
        
        if not os.path.exists(pcx_filename):
            raise ValueError(f'Unable to find the texture for this quake model: {pcx_filename}')
                
        return pcx_filename
        