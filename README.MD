# Caduceus

Caduceus is a simple Python Quake Model Viewer. It supports version 2 (IDP2) of the Quake Model format. This is a port of a project I wrote for the very first version of C# in ~2000, prior to PDC 2000 where it was demoed in the Advanced C# talk. I recently started to learn Python and this seemed like a fun project. I kept much of the display code as it was originally instead of using a 3d library. My hope was to better understand how Python handles data types, matricies, and arrays. I also experimented with Pylance for type annotations.

![An animated gif displaying a model named forgottenone being animated through various sequences both wireframe and texutre mapped in Caduceus](imgs/Caduceus.gif)

## Command line

Caduceus requires two command line arguments. The first is to the main Quake model file, usually a file named 'tris.md2'. The second is to the weapon for that same Quake model file, usually a file named 'weapon.md2'. Pcx files named tris.pcx and weapon.pcx must be colocated with those files or an exception will be thrown. 

Usage:

```python main.py tris.md2 weapon.md2```

## Interaction

Caduceus supports the following keyboard interactions:
* Press `w` to switch to wireframe rendering (the default)
* Press `t` to switch to texture mapped rendering
* Press `+` or scroll up on the mouse wheel to increase the scale of the model
* Press `-` or scroll down on the mouse wheel to decrease the scale of the model
* Press the `right arrow` key to advance forward in the list of sequences encoded in the model
* Press the `left arrow` key to move backwards in the list of sequences encoded in the model
* Right-click and move the mouse to change the Z rotation (around the vertical axis)