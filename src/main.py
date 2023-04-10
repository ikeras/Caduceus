import argparse
import dataclasses as dc
import math as m
from typing import Tuple
import sys

import numpy as np
import pygame

from character import Character
from graphics import Graphics
from point2d import Point2d
from render_type import RenderType

buffer = np.zeros((1000, 1000), dtype=np.uint32)

def draw_character_frame(graphics: Graphics, character: Character, surface: pygame.Surface):
    """Renders all of the triangles in the character's current frame to the surface.

    Args:
        graphics (Graphics): A graphics object used to draw textured triangles.
        character (Character): The character to render.
        surface (pygame.Surface): The surface to render the character to.
    """
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

def get_centered_sequence_name(character: Character, font: pygame.font.Font) -> Tuple[pygame.Surface, pygame.Rect]:
    """Creates a surface and rect for the character's sequence name centered on the screen.

    Args:
        character (Character): The character to get the sequence name from.
        font (pygame.font.Font): The font to use for the text.

    Returns:
        Tuple[pygame.Surface, pygame.Rect]: The surface and rect for the text.
    """
    text_surface = font.render(character.sequence_name, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.centerx = 500
    
    return text_surface, text_rect

def main():
    """A simple viewer for Quake model version 2 md2 files."""
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
    
    font = pygame.font.Font(None, 30)    
    text_surface, text_rect = get_centered_sequence_name(character, font)
    
    fps = pygame.time.Clock()
    display_surface = pygame.Surface((1000, 1000))
    starting_mouse_pos = (0, 0)
    rotating = False

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
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    character.scale(character.size + 0.5)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    character.scale(character.size - 0.5)
                elif event.key == pygame.K_RIGHT:
                    character.advance_sequence()
                    text_surface, text_rect = get_centered_sequence_name(character, font)
                elif event.key == pygame.K_LEFT:
                    character.previous_sequence()
                    text_surface, text_rect = get_centered_sequence_name(character, font)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    rotating = True
                    starting_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4:
                    character.scale(character.size + 0.5)
                elif event.button == 5:
                    character.scale(character.size - 0.5)                
            elif event.type == pygame.MOUSEMOTION:
                if rotating:
                    new_mouse_pos = pygame.mouse.get_pos()
                    rotate_z = (character.rotate_z + new_mouse_pos[0] - starting_mouse_pos[0]) % 360
                    character.rotate(character.rotate_x, character.rotate_y, rotate_z)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    new_mouse_pos = pygame.mouse.get_pos()
                    rotate_z = (character.rotate_z + new_mouse_pos[0] - starting_mouse_pos[0]) % 360
                    character.rotate(character.rotate_x, character.rotate_y, rotate_z)
                    rotating = False

        character.advance_frame()
        draw_character_frame(graphics, character, display_surface)
        display_surface.blit(text_surface, text_rect)
        pygame.Surface.blit(pygame.display.get_surface(), display_surface, (0,0))
        pygame.display.update()
        
        fps.tick(60)

main()