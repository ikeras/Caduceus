import math as m

import numpy as np

def rotate_x(angle):
    theta = np.deg2rad(angle)
    return np.array([[ 1, 0           , 0           ],
                    [ 0, m.cos(theta),-m.sin(theta)],
                    [ 0, m.sin(theta), m.cos(theta)]])

def rotate_y(angle):
    theta = np.deg2rad(angle)
    return np.array([[ m.cos(theta), 0, m.sin(theta)],
                    [ 0           , 1, 0           ],
                    [-m.sin(theta), 0, m.cos(theta)]])

def rotate_z(angle):
    theta = np.deg2rad(angle)
    return np.array([[ m.cos(theta), -m.sin(theta), 0 ],
                    [ m.sin(theta), m.cos(theta) , 0 ],
                    [ 0           , 0            , 1 ]])