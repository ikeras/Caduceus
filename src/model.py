from collections import namedtuple
from io import BufferedReader
import re
import struct
from typing import Generator, List, Tuple

from nptyping import NDArray, Shape, Float32
import numpy as np

from face import Face
from pcx import Pcx
from point2d import Point2d
import linear_algebra as la
from render_type import RenderType
from textured_triangle import TexturedTriangle

class QuakeModel:
    Header = namedtuple('Header', 'skin_width skin_height frame_size num_skins num_vertices num_tex_coords num_faces num_gl_commands num_frames offset_skins offset_tex_coords offset_faces offset_frames offset_gl_commands offset_end')
    TexturedFace = namedtuple('TexturedFace', 'point_1 point_2 point_3 tex_index_1 tex_index_2 tex_index_3')
    SkinTextureOffset = namedtuple('SkinTextureOffset', 's t')
    TriangleVertex = namedtuple('TriangleVertex', 'x y z light_normal_index')
    AnimationFrame = namedtuple('AnimationFrame', 'name frame_data normals')
    Sequence = namedtuple('Sequence', 'name start_frame num_frames')
    
    VIEWING_DISTANCE = -1500
    
    def __init__(self, render_type: RenderType):
        self._frame = 0
        self._render_type = render_type
        self._sequence = 0
        
    @property
    def render_type(self) -> RenderType:
        return self._render_type
    
    @render_type.setter
    def render_type(self, render_type: RenderType) -> None:
        self._render_type = render_type
        
    @property
    def sequence_name(self) -> str:
        return self._sequences[self._sequence].name        
    
    def from_file(self, quake_filename: str, pcx_filename: str) -> None:
        with open(quake_filename, 'rb') as f:
            id = f.read(4)
            version = f.read(4)
            
            if id != b'IDP2' or version != b'\x08\x00\x00\x00':
                raise ValueError('Only Quake 2 models are supported')
            
            self.header = self._read_header(f)
            self.texture = Pcx()
            self.texture.from_file(pcx_filename)
            self._texture_offsets = self._read_texture_offsets(f)
            self._triangles = self._read_faces(f)
            self._read_animation_frames(f)
            
            self._world_coordinates = np.zeros((self.header.num_vertices, 3), dtype=np.float32)
            self._should_rotate = np.zeros(self.header.num_vertices, dtype=np.bool_)
    
    def advance_frame(self) -> None:
        self._frame += 1
        
        if self._frame >= self._sequences[self._sequence].start_frame + self._sequences[self._sequence].num_frames:
            self._frame = self._sequences[self._sequence].start_frame        
    
    def advance_sequence(self) -> None:
        self._sequence = self._sequence + 1 if self._sequence + 1 < len(self._sequences) else 0
        self._frame = self._sequences[self._sequence].start_frame
    
    def previous_sequence(self) -> None:
        self._sequence = self._sequence + -1 if self._sequence + -1 > 0 else len(self._sequences) - 1
        self._frame = self._sequences[self._sequence].start_frame    
    
    def rotate(self, angle_x: int, angle_y: int, angle_z: int) -> None:
        self._rotation = (angle_x, angle_y, angle_z)
        
    def scale(self, scale: float) -> None:
        self._scale = scale
        
    def translate(self, x: int, y: int, z: int) -> None:
        self._translation = (x, y, z)
        
    def triangle_in_frame(self) -> Generator[TexturedTriangle, None, None]:
        num_faces_visible = 0
        
        frame = self._frames[self._frame]
        visible_faces = []
        
        object_viewer = (0, 150, 0) @ la.rotate_x(self._rotation[0]) @ la.rotate_y(self._rotation[1]) @ la.rotate_z(self._rotation[2])

        if self._render_type == RenderType.WIREFRAME:
            self._should_rotate.fill(True)
            visible_faces = self._triangles
        else:
            self._should_rotate.fill(False)
            for face_index in range(self.header.num_faces):
                if np.dot(object_viewer, frame.normals[face_index]) < 0:
                    num_faces_visible += 1
                    self._should_rotate[self._triangles[face_index].point_1] = True
                    self._should_rotate[self._triangles[face_index].point_2] = True
                    self._should_rotate[self._triangles[face_index].point_3] = True
                    visible_faces.append(self._triangles[face_index])
        
        self._apply_transformations()
        
        for face in visible_faces:
            z_center = self._world_coordinates[face.point_1][1] + \
                       self._world_coordinates[face.point_2][1] + \
                       self._world_coordinates[face.point_3][1] / 3
            
            vertex_1 = Point2d(int(self._world_coordinates[face.point_1][0] / \
                               self._world_coordinates[face.point_1][1] * \
                               QuakeModel.VIEWING_DISTANCE),
                               int(self._world_coordinates[face.point_1][2] / \
                               self._world_coordinates[face.point_1][1] * \
                               QuakeModel.VIEWING_DISTANCE))
            
            vertex_2 = Point2d(int(self._world_coordinates[face.point_2][0] / \
                               self._world_coordinates[face.point_2][1] * \
                               QuakeModel.VIEWING_DISTANCE),
                               int(self._world_coordinates[face.point_2][2] / \
                               self._world_coordinates[face.point_2][1] * \
                               QuakeModel.VIEWING_DISTANCE))

            vertex_3 = Point2d(int(self._world_coordinates[face.point_3][0] / \
                               self._world_coordinates[face.point_3][1] * \
                               QuakeModel.VIEWING_DISTANCE),
                               int(self._world_coordinates[face.point_3][2] / \
                               self._world_coordinates[face.point_3][1] * \
                               QuakeModel.VIEWING_DISTANCE))
            
            skin_vertex_1 = Point2d(self._texture_offsets[face.tex_index_1].s, \
                                    self._texture_offsets[face.tex_index_1].t)
            
            skin_vertex_2 = Point2d(self._texture_offsets[face.tex_index_2].s, \
                                    self._texture_offsets[face.tex_index_2].t)            
            
            skin_vertex_3 = Point2d(self._texture_offsets[face.tex_index_3].s, \
                                    self._texture_offsets[face.tex_index_3].t)            

            yield TexturedTriangle(z_center, Face([vertex_1, vertex_2, vertex_3], [skin_vertex_1, skin_vertex_2, skin_vertex_3], self.texture))
   
    def _calculate_normals(self, frame_data: List[TriangleVertex]) -> NDArray[Shape['*, 3'], Float32]:
        u = np.empty((self.header.num_faces, 3), dtype=np.float32)
        v = np.empty((self.header.num_faces, 3), dtype=np.float32)
        
        for face_index in range(self.header.num_faces):
            u[face_index] = [frame_data[self._triangles[face_index].point_2].x - \
                             frame_data[self._triangles[face_index].point_1].x, \
                             frame_data[self._triangles[face_index].point_2].y - \
                             frame_data[self._triangles[face_index].point_1].y, \
                             frame_data[self._triangles[face_index].point_2].z - \
                             frame_data[self._triangles[face_index].point_1].z]

            v[face_index] = [frame_data[self._triangles[face_index].point_3].x - \
                             frame_data[self._triangles[face_index].point_2].x, \
                             frame_data[self._triangles[face_index].point_3].y - \
                             frame_data[self._triangles[face_index].point_2].y, \
                             frame_data[self._triangles[face_index].point_3].z - \
                             frame_data[self._triangles[face_index].point_2].z]

        return np.cross(u, v)
    
    def _read_header(self, f: BufferedReader) -> Header:
        data = f.read(60)
        return QuakeModel.Header._make(struct.unpack('<15i', data))

    def _read_texture_offsets(self, f: BufferedReader) -> List[SkinTextureOffset]:
        f.seek(self.header.offset_tex_coords)
        data = f.read(self.header.num_tex_coords * 4)
        return [QuakeModel.SkinTextureOffset._make(struct.unpack('<2h', data[i:i+4])) for i in range(0, len(data), 4)]

    def _read_faces(self, f: BufferedReader) -> List[TexturedFace]:
        f.seek(self.header.offset_faces)
        data = f.read(self.header.num_faces * 12)
        return [QuakeModel.TexturedFace._make(struct.unpack('<6h', data[i:i+12])) for i in range(0, len(data), 12)]
    
    def _read_animation_frame(self, data: bytes, frame_index: int) -> Tuple[str, List[TriangleVertex]]:
            scale_x, scale_y, scale_z, translate_x, translate_y, translate_z, name = struct.unpack('<6f16s', data[frame_index * self.header.frame_size:frame_index * self.header.frame_size + 40])
            name = name.decode('utf-8').strip('\x00')
            name = re.sub(r'[^a-zA-Z]', '', name)
            
            frame_data = []            
            for unpack_frame_index in range(self.header.num_vertices):
                x, y, z, light_normal_index = struct.unpack('<4B', data[frame_index * self.header.frame_size + 40 + unpack_frame_index * 4:frame_index * self.header.frame_size + 40 + unpack_frame_index * 4 + 4])
                x = x * scale_x + translate_x
                y = y * scale_y + translate_y
                z = z * scale_z + translate_z
                frame_data.append(QuakeModel.TriangleVertex._make((x, y, z, light_normal_index)))
                
            return name, frame_data
    
    def _read_animation_frames(self, f: BufferedReader) -> None:
        f.seek(self.header.offset_frames)
        data = f.read(self.header.num_frames * self.header.frame_size)
        
        last_group_name = ''
        name = ''
        self._sequences = []
        num_sequences = 0
        self._frames = []
        
        for frame_index in range(self.header.num_frames):            
            name, frame_data = self._read_animation_frame(data, frame_index)
            normals = self._calculate_normals(frame_data)
            self._frames.append(QuakeModel.AnimationFrame._make((name, frame_data, normals)))
            
            if last_group_name != name:
                self._sequences.append(QuakeModel.Sequence._make((name, frame_index, 0)))
                
                if num_sequences > 0:
                    self._sequences[num_sequences - 1] = self._sequences[num_sequences - 1]._replace(num_frames = frame_index - self._sequences[num_sequences - 1].start_frame)
                
                num_sequences += 1
                last_group_name = name

        
        self._sequences[num_sequences - 1] = self._sequences[num_sequences - 1]._replace(num_frames = self.header.num_frames - self._sequences[num_sequences - 1].start_frame)
        
    def _apply_transformations(self):
        rotate = la.rotate_x(self._rotation[0]) @ la.rotate_y(self._rotation[1]) @ la.rotate_z(self._rotation[2])
        
        frame = self._frames[self._frame]
        
        for index in range(self.header.num_vertices):
            if self._should_rotate[index]:
                x = frame.frame_data[index].x * self._scale * rotate[0, 0] + \
                    frame.frame_data[index].y * self._scale * rotate[1, 0] + \
                    frame.frame_data[index].z * self._scale * rotate[2, 0] + \
                    self._translation[0]
                                                    
                y = frame.frame_data[index].x * self._scale * rotate[0, 1] + \
                    frame.frame_data[index].y * self._scale * rotate[1, 1] + \
                    frame.frame_data[index].z * self._scale * rotate[2, 1] + \
                    self._translation[1]
                
                z = frame.frame_data[index].x * self._scale * rotate[0, 2] + \
                    frame.frame_data[index].y * self._scale * rotate[1, 2] + \
                    frame.frame_data[index].z * self._scale * rotate[2, 2] + \
                    self._translation[2]
                
                self._world_coordinates[index] = (x, y, z)   
            