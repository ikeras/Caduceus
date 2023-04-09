import argparse
import dataclasses as dc
import math as m
import os
import sys

import numpy as np
import pygame
from pygame.locals import *

from character import Character
from graphics import Graphics
from point2d import Point2d
from render_type import RenderType

buffer = np.zeros((1000, 1000), dtype=np.uint32)

def draw_character_frame(graphics: Graphics, character: Character, surface: pygame.Surface):
    triangles = sorted(character.triangle_in_frame(), key=lambda triangle: triangle.z_center)
    
    if character.render_type == RenderType.TEXTURED:
        buffer = np.zeros((1000, 1000), dtype=np.uint32)
        for triangle in triangles:
            graphics.draw_textured_triangle(triangle.face, buffer)
        pygame.surfarray.blit_array(surface, buffer)
    else:
        surface.fill(0)
        for triangle in triangles:
            pygame.draw.line(surface, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[0]), dc.astuple(triangle.face.triangle_verts[1]))
            pygame.draw.line(surface, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[1]), dc.astuple(triangle.face.triangle_verts[2]))
            pygame.draw.line(surface, (255, 255, 255), dc.astuple(triangle.face.triangle_verts[2]), dc.astuple(triangle.face.triangle_verts[0]))

def main():  
    parser = argparse.ArgumentParser(description='Quake model viewer')
    parser.add_argument('quake_model', help='Quake model verison 2 md2 file for the character')
    parser.add_argument('weapon_model', help='Quake model verison 2 md2 file for the weapon')
    args = parser.parse_args()
    
    character = Character(RenderType.WIREFRAME, args.quake_model, args.weapon_model)
      
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
                    character.render_type = RenderType.WIREFRAME
                elif event.key == pygame.K_t:
                    character.render_type = RenderType.TEXTURED

        character.advance_frame()
        draw_character_frame(graphics, character, display_surface)
        pygame.Surface.blit(pygame.display.get_surface(), display_surface, (0,0))
        pygame.display.update()
        
        fps.tick(60)

main()