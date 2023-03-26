import argparse
import dataclasses as dc
import math as m
import os
import sys

import numpy as np
import pygame
from pygame.locals import *

from model import QuakeModel

def draw_model_frame(model: QuakeModel, buffer):
    triangles = []
    
    for triangle in model.triangle_in_frame():
        triangles.append(triangle)
  
    triangles.sort(key=lambda triangle: triangle.z_center, reverse=True)
    
    for triangle in triangles:
        pygame.draw.line(buffer, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[0]), dc.astuple(triangle.face.triangle_verts[1]))
        pygame.draw.line(buffer, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[1]), dc.astuple(triangle.face.triangle_verts[2]))
        pygame.draw.line(buffer, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[2]), dc.astuple(triangle.face.triangle_verts[0]))
  
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
    model.rotate(0, 180, 90)
    model.translate(70, -250, 70)
    model.scale(1)
      
    pygame.init()
    pygame.display.set_caption("Quake model viewer")
    pygame.display.set_mode((1000, 1000), DOUBLEBUF)
    
    fps = pygame.time.Clock()
    buffer = pygame.Surface((1000, 1000))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()        
        
        model.advance_frame()
        buffer.fill((0, 0, 0))
        draw_model_frame(model, buffer)
        pygame.Surface.blit(pygame.display.get_surface(), buffer, (0,0))
        pygame.display.update()
        
        fps.tick()

main()