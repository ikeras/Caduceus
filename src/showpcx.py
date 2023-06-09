import argparse
import os
import sys

import numpy as np
import pygame

from pcx import Pcx

def main():  
    """A simple program to view a pcx file from a Quake model.

    Raises:
        ValueError: If there isn't a texture file for the model.
    """
    parser = argparse.ArgumentParser(description='Quake model viewer')
    parser.add_argument('quake_model', help='Quake model verison 2 md2 file')
    args = parser.parse_args()
    
    quake_filename = args.quake_model
    base_name, _ = os.path.splitext(quake_filename)
    pcx_filename = base_name + '.pcx'
    
    if not os.path.exists(pcx_filename):
        raise ValueError(f'Unable to find the texture for this quake model: {pcx_filename}')
    
    pcx = Pcx()
    pcx.from_file(pcx_filename)
           
    pygame.init()
    pygame.display.set_caption("Quake model viewer")
    pygame.display.set_mode((1000, 1000))
    
    fps = pygame.time.Clock()
    
    buffer = np.zeros((1000, 1000), dtype=np.uint32)
    display_surface = pygame.Surface((1000, 1000))
    
    for y in range(pcx.height):
        for x in range(pcx.width):
            red, green, blue = pcx.palette[pcx.image_data[x, y]]
            buffer[x, y] = 0xFF000000 | red << 16 | green << 8 | blue
                           
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.surfarray.blit_array(display_surface, buffer)
        pygame.Surface.blit(pygame.display.get_surface(), display_surface, (0,0))
        pygame.display.update()
        
        fps.tick(60)

main()