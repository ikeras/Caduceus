import os
from typing import Generator

from model import QuakeModel
from render_type import RenderType
from textured_triangle import TexturedTriangle

class Character:
    def __init__(self, render_type: RenderType, quake_filename: str, weapon_filename: str):
        """The constructor for the Character class.

        Args:
            render_type (RenderType): Whether to render the character as textured or wireframe.
            quake_filename (str): The full path to the Quake model version 2 md2 file for the character.
            weapon_filename (str): The full path to the Quake model version 2 md2 file for the weapon.
        """
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
        """The render type for the character."""
        return self._model.render_type

    @render_type.setter
    def render_type(self, render_type: RenderType) -> None:
        self._model.render_type = render_type
        self._weapon.render_type = render_type

    @property
    def rotate_x(self) -> int:
        """The rotation angle around the x-axis in degrees."""
        return self._rotate_x

    @property
    def rotate_y(self) -> int:
        """The rotation angle around the y-axis in degrees."""
        return self._rotate_y

    @property
    def rotate_z(self) -> int:
        """The rotation angle around the z-axis in degrees."""        
        return self._rotate_z
    
    @property
    def size(self) -> float:
        """The scale factor for the character."""
        return self._size
        
    @property
    def sequence_name(self) -> str:
        """The name of the current sequence."""
        return self._model.sequence_name
     
    def advance_frame(self) -> None:
        """Advance the current frame in the current sequence. If the current frame is the last frame in the sequence, then the current frame will be set to the first frame in the sequence."""
        self._model.advance_frame()
        self._weapon.advance_frame()
    
    def advance_sequence(self) -> None:
        """Advance the current sequence. If the current sequence is the last sequence, then the current sequence will be set to the first sequence."""
        self._model.advance_sequence()
        self._weapon.advance_sequence()
        
    def previous_sequence(self) -> None:
        """Go back to the previous sequence. If the current sequence is the first sequence, then the current sequence will be set to the last sequence."""
        self._model.previous_sequence()
        self._weapon.previous_sequence()        
            
    def rotate(self, angle_x: int, angle_y: int, angle_z: int) -> None:
        """Rotate the character around the x, y, and z axes.

        Args:
            angle_x (int): The rotation angle around the x-axis in degrees.
            angle_y (int): The rotation angle around the y-axis in degrees.
            angle_z (int): The rotation angle around the z-axis in degrees.
        """
        self._rotate_x = angle_x
        self._rotate_y = angle_y
        self._rotate_z = angle_z
        self._model.rotate(angle_x, angle_y, angle_z)
        self._weapon.rotate(angle_x, angle_y, angle_z)
    
    def scale(self, scale: float) -> None:
        """Set the scale factor for the character.

        Args:
            scale (float): The scale factor for the character.
        """
        self._size = scale
        self._model.scale(scale)
        self._weapon.scale(scale)
        
    def translate(self, x: int, y: int, z: int) -> None:
        """Translate the character in the x, y, and z directions.

        Args:
            x (int): The translation in the x direction.
            y (int): The translation in the y direction.
            z (int): The translation in the z direction.
        """
        self._model.translate(x, y, z)
        self._weapon.translate(x, y, z)
    
    def triangle_in_frame(self) -> Generator[TexturedTriangle, None, None]:
        """Yield the triangles in the current frame for the character."""
        for triangle in self._model.triangle_in_frame():
            yield triangle
        
        for triangle in self._weapon.triangle_in_frame():
            yield triangle
        
    @staticmethod
    def _get_pcx_filename(filename: str) -> str:
        """A static method to get the pcx filename for the given filename.

        Args:
            filename (str): The full path to the Quake model version 2 md2 file.

        Raises:
            ValueError: If the pcx file does not exist.

        Returns:
            str: The full path to the pcx file.
        """
        base_name, _ = os.path.splitext(filename)
        pcx_filename = base_name + '.pcx'
        
        if not os.path.exists(pcx_filename):
            raise ValueError(f'Unable to find the texture for this quake model: {pcx_filename}')
                
        return pcx_filename