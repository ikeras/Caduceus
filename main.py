import argparse
import dataclasses as dc
import math as m
import os
import sys

import numpy as np
import pygame
from pygame.locals import *

from graphics import Graphics
from model import QuakeModel
from point2d import Point2d
from render_type import RenderType

buffer = np.zeros((1000, 1000), dtype=np.uint32)

def draw_model_frame(graphics: Graphics, model: QuakeModel, surface: pygame.Surface):
    global buffer
    
    triangles = []
    
    for triangle in model.triangle_in_frame():
        triangles.append(triangle)
  
    triangles.sort(key=lambda triangle: triangle.z_center)
    
    if model.render_type == RenderType.TEXTURED:
        buffer.fill(0)
    else:
        surface.fill(0)
        
    for triangle in triangles:
        if model.render_type == RenderType.TEXTURED:
            graphics.draw_textured_triangle(triangle.face, buffer)
        else:
            pygame.draw.line(surface, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[0]), dc.astuple(triangle.face.triangle_verts[1]))
            pygame.draw.line(surface, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[1]), dc.astuple(triangle.face.triangle_verts[2]))
            pygame.draw.line(surface, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[2]), dc.astuple(triangle.face.triangle_verts[0]))
    
    if model.render_type == RenderType.TEXTURED:
        pygame.surfarray.blit_array(surface, buffer)

def main():  
    parser = argparse.ArgumentParser(description='Quake model viewer')
    parser.add_argument('quake_model', help='Quake model verison 2 md2 file')
    args = parser.parse_args()
    
    quake_filename = args.quake_model
    base_name, _ = os.path.splitext(quake_filename)
    pcx_filename = base_name + '.pcx'
    
    if not os.path.exists(pcx_filename):
        raise ValueError(f'Unable to find the texture for this quake model: {pcx_filename}')
    
    model = QuakeModel(RenderType.WIREFRAME)
    model.from_file(quake_filename, pcx_filename)
    model.rotate(0, 180, 90)
    model.translate(70, -250, 70)
    model.scale(1)
      
    graphics = Graphics()
    graphics.set_clip(Point2d(0, 0), Point2d(1000, 1000))
      
    pygame.init()
    pygame.display.set_caption("Quake model viewer")
    pygame.display.set_mode((1000, 1000))
    
    fps = pygame.time.Clock()
    display_surface = pygame.Surface((1000, 1000))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    model.render_type = RenderType.WIREFRAME
                elif event.key == pygame.K_t:
                    model.render_type = RenderType.TEXTURED

        model.advance_frame()
        draw_model_frame(graphics, model, display_surface)
        pygame.Surface.blit(pygame.display.get_surface(), display_surface, (0,0))
        pygame.display.update()
        
        fps.tick(60)

main()