import math as m

from nptyping import NDArray, Shape, Float32
import numpy as np

def rotate_x(angle: int) -> NDArray[Shape['3,3'], Float32]:
    theta = np.deg2rad(angle)
    return np.array([[ 1, 0           , 0           ],
                    [ 0, m.cos(theta),-m.sin(theta)],
                    [ 0, m.sin(theta), m.cos(theta)]])

def rotate_y(angle: int) -> NDArray[Shape['3,3'], Float32]:
    theta = np.deg2rad(angle)
    return np.array([[ m.cos(theta), 0, m.sin(theta)],
                    [ 0           , 1, 0           ],
                    [-m.sin(theta), 0, m.cos(theta)]])

def rotate_z(angle: int) -> NDArray[Shape['3,3'], Float32]:
    theta = np.deg2rad(angle)
    return np.array([[ m.cos(theta), -m.sin(theta), 0 ],
                    [ m.sin(theta), m.cos(theta) , 0 ],
                    [ 0           , 0            , 1 ]])