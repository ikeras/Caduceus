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

def draw_model_frame(graphics: Graphics, model: QuakeModel, buffer):
    triangles = []
    
    for triangle in model.triangle_in_frame():
        triangles.append(triangle)
  
    triangles.sort(key=lambda triangle: triangle.z_center)
    
    for triangle in triangles:
        graphics.draw_textured_triangle(triangle.face, buffer)
    
    # for triangle in triangles:
    #     pygame.draw.line(buffer, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[0]), dc.astuple(triangle.face.triangle_verts[1]))
    #     pygame.draw.line(buffer, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[1]), dc.astuple(triangle.face.triangle_verts[2]))
    #     pygame.draw.line(buffer, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[2]), dc.astuple(triangle.face.triangle_verts[0]))
  
def main():  
    parser = argparse.ArgumentParser(description='Quake model viewer')
    parser.add_argument('quake_model', help='Quake model verison 2 md2 file')
    args = parser.parse_args()
    
    quake_filename = args.quake_model
    base_name, _ = os.path.splitext(quake_filename)
    pcx_filename = base_name + '.pcx'
    
    if not os.path.exists(pcx_filename):
        raise ValueError(f'Unable to find the texture for this quake model: {pcx_filename}')
    
    model = QuakeModel()
    model.from_file(quake_filename, pcx_filename)
    model.rotate(270, 180, 90)
    model.translate(70, -250, 70)
    model.scale(1)
      
    graphics = Graphics()
    graphics.set_clip(Point2d(0, 0), Point2d(1000, 1000))
      
    pygame.init()
    pygame.display.set_caption("Quake model viewer")
    pygame.display.set_mode((1000, 1000), DOUBLEBUF)
    
    fps = pygame.time.Clock()
    # buffer = pygame.Surface((1000, 1000))    
    buffer = np.zeros((1000, 1000), dtype=np.uint32)    
    display_surface = pygame.Surface((1000, 1000), DOUBLEBUF)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    model.advance_frame()
                    
        buffer.fill(0)
        draw_model_frame(graphics, model, buffer)
        pygame.surfarray.blit_array(display_surface, buffer)
        pygame.Surface.blit(pygame.display.get_surface(), display_surface, (0,0))
        pygame.display.update()
        
        fps.tick(60)

main()