import sys

from nptyping import NDArray, UInt32, Shape
import numpy as np

from edge_scan import EdgeScan
from face import Face
from point2d import Point2d

class Graphics:
    def draw_textured_triangle(self, face: Face, buffer: NDArray[Shape['*,*'], UInt32]) -> None:
        done = False
        min_y: int
        max_y: int
        min_vert: int
        max_vert: int
        dest_y: int
        count: int
        
        left_edge = EdgeScan()
        right_edge = EdgeScan()
        
        min_y = sys.maxsize
        max_y = -sys.maxsize - 1
        min_vert = 0
        max_vert = 0
        
        for count in range(3):
            if face.triangle_verts[count].y < min_y:
                min_y = round(face.triangle_verts[count].y)
                min_vert = count
            if face.triangle_verts[count].y > max_y:
                max_y = round(face.triangle_verts[count].y)
                max_vert = count
        
        if min_y >= max_y:
            return
        
        dest_y = min_y
        
        left_edge.direction = -1
        self._set_up_edge(left_edge, face, min_vert, max_vert)
        right_edge.direction = 1
        self._set_up_edge(right_edge, face, min_vert, max_vert)
        
        while not done:
            if dest_y >= self._max.y:
                return
            
            if dest_y >= self._min.y:
                self._scan_out_line(face, left_edge, right_edge, buffer, dest_y)
            
            if not self._step_edge(left_edge, face, max_vert):
                return
            
            if not self._step_edge(right_edge, face, max_vert):
                return
            
            dest_y += 1
    
    def set_clip(self, min: Point2d, max: Point2d):
        self._min = min
        self._max = max
                
    def _set_up_edge(self, edge: EdgeScan, face: Face, start_vertex: int, max_vertex: int) -> bool:
        done = False
        next_vertex: int
        dest_x_width: int
        dest_y_height: float
        
        while not done:
            if start_vertex == max_vertex:
                return False
            
            next_vertex = start_vertex + edge.direction
            if next_vertex > 2:
                next_vertex = 0
            elif next_vertex < 0:
                next_vertex = 2
            
            edge.remaining_scans = round(face.triangle_verts[next_vertex].y - face.triangle_verts[start_vertex].y)
            if edge.remaining_scans != 0:
                dest_y_height = edge.remaining_scans
                edge.current_end = next_vertex
                edge.source_x = face.skin_verts[start_vertex].x
                edge.source_y = face.skin_verts[start_vertex].y
                edge.source_step_x = (face.skin_verts[next_vertex].x - edge.source_x) / dest_y_height
                edge.source_step_y = (face.skin_verts[next_vertex].y - edge.source_y) / dest_y_height
                edge.dest_x = round(face.triangle_verts[start_vertex].x)
                dest_x_width = face.triangle_verts[next_vertex].x - face.triangle_verts[start_vertex].x
                
                if dest_x_width < 0:
                    edge.dest_x_direction = -1
                    dest_x_width = -dest_x_width
                    edge.dest_x_error_term = 1 - edge.remaining_scans
                    edge.dest_x_int_step = -(dest_x_width // edge.remaining_scans)
                else:
                    edge.dest_x_direction = 1
                    edge.dest_x_error_term = 0
                    edge.dest_x_int_step = dest_x_width // edge.remaining_scans
                
                edge.dest_x_adj_up = round(dest_x_width % edge.remaining_scans)
                edge.dest_x_adj_down = edge.remaining_scans
                done = True

            start_vertex = next_vertex
        
        return True
    
    def _step_edge(self, edge: EdgeScan, face: Face, max_vertex: int) -> bool:
        edge.remaining_scans -= 1
        
        if edge.remaining_scans <= 0:
            return self._set_up_edge(edge, face, edge.current_end, max_vertex)
        
        edge.source_x += edge.source_step_x
        edge.source_y += edge.source_step_y
        edge.dest_x += edge.dest_x_int_step
        edge.dest_x_error_term += edge.dest_x_adj_up
        
        if edge.dest_x_error_term > 0:
            edge.dest_x += edge.dest_x_direction
            edge.dest_x_error_term -= edge.dest_x_adj_down
            
        return True
    
    def _scan_out_line(self, face: Face, left_edge: EdgeScan, right_edge: EdgeScan, buffer: NDArray[Shape['*,*'], UInt32], dest_y: int) -> None:
        source_x: float
        source_y: float
        dest_width: float
        source_step_x: float
        source_step_y: float
        dest_x: int
        dest_x_max: int
        count: int
        
        dest_x = left_edge.dest_x
        dest_x_max = right_edge.dest_x
        
        if dest_x_max <= self._min.x or dest_x > self._max.x:
            return
        
        if (dest_x_max - dest_x) <= 0:
            return
        
        source_x = left_edge.source_x
        source_y = left_edge.source_y
        
        dest_width = dest_x_max - dest_x
        source_step_x = (right_edge.source_x - source_x) / dest_width
        source_step_y = (right_edge.source_y - source_y) / dest_width
        
        source_x += source_step_x * 0.5
        source_y += source_step_y * 0.5
        
        if dest_x_max > self._max.x:
            dest_x_max = self._max.x
        
        if dest_x < self._min.x:
            count = self._min.x - dest_x
            source_x += source_step_x * count
            source_y += source_step_y * count
            dest_x = self._min.x
        
        for count in range(round(dest_x), round(dest_x_max)):
            color = face.texture.palette[face.texture.image_data[round(source_x), round(source_y)]]
            buffer[round(dest_y), count] = 0xFF000000 | (color[0] << 16) | (color[1] << 8) | color[2]
        
            source_x += source_step_x
            source_y += source_step_y
        