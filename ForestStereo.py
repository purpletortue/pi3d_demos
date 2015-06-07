#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" ForestWalk but with binocular view - i.e. for google cardboard

NB in this example the cameras have been set with a negative separation i.e.
for viewing cross-eyed as most people find this easier without a viewer!!!
If a viewer is used then the line defining CAMERA would need to be changed
to an appropriate +ve separation.

NB also, no camera has been explicitly assigned to the objects so they all
use the default instance and this will be CAMERA.camera_3d so long as the
StereoCam instance was created before any other Camera instance.
"""

import math,random

import demo
import pi3d

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=200, y=200)
DISPLAY.set_background(0.4,0.8,0.8,1)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol=(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))

CAMERA = pi3d.StereoCam(separation=-0.5) # negative for cross-eyed!
#========================================

# load shader
shader = pi3d.Shader("uv_bump")
shinesh = pi3d.Shader("uv_reflect")
flatsh = pi3d.Shader("uv_flat")

tree2img = pi3d.Texture("textures/tree2.png")
tree1img = pi3d.Texture("textures/tree1.png")
hb2img = pi3d.Texture("textures/hornbeam2.png")
bumpimg = pi3d.Texture("textures/grasstile_n.jpg")
reflimg = pi3d.Texture("textures/stars.jpg")
rockimg = pi3d.Texture("textures/rock1.jpg")

FOG = ((0.3, 0.3, 0.4, 0.8), 650.0)
TFOG = ((0.2, 0.24, 0.22, 1.0), 150.0)

#myecube = pi3d.EnvironmentCube(900.0,"HALFCROSS")
ectex=pi3d.loadECfiles("textures/ecubes","sbox")
myecube = pi3d.EnvironmentCube(size=900.0, maptype="FACES", name="cube")
myecube.set_draw_details(flatsh, ectex)

# Create elevation map
mapsize = 1000.0
mapheight = 60.0
mountimg1 = pi3d.Texture("textures/mountains3_512.jpg")
mymap = pi3d.ElevationMap("textures/mountainsHgt.png", name="map",
                     width=mapsize, depth=mapsize, height=mapheight,
                     divx=32, divy=32) 
mymap.set_draw_details(shader, [mountimg1, bumpimg, reflimg], 128.0, 0.0)
mymap.set_fog(*FOG)

#Create tree models
treeplane = pi3d.Plane(w=4.0, h=5.0)

treemodel1 = pi3d.MergeShape(name="baretree")
treemodel1.add(treeplane.buf[0], 0,0,0)
treemodel1.add(treeplane.buf[0], 0,0,0, 0,90,0)

treemodel2 = pi3d.MergeShape(name="bushytree")
treemodel2.add(treeplane.buf[0], 0,0,0)
treemodel2.add(treeplane.buf[0], 0,0,0, 0,60,0)
treemodel2.add(treeplane.buf[0], 0,0,0, 0,120,0)

#Scatter them on map using Merge shape's cluster function
mytrees1 = pi3d.MergeShape(name="trees1")
mytrees1.cluster(treemodel1.buf[0], mymap, 0.0, 0.0, 400.0, 400.0, 50, "", 8.0, 3.0)
mytrees1.set_draw_details(flatsh, [tree2img], 0.0, 0.0)
mytrees1.set_fog(*TFOG)

mytrees2 = pi3d.MergeShape(name="trees2")
mytrees2.cluster(treemodel2.buf[0], mymap, 0.0, 0.0, 400.0, 400.0, 80, "", 6.0, 3.0)
mytrees2.set_draw_details(flatsh, [tree1img], 0.0, 0.0)
mytrees2.set_fog(*TFOG)

mytrees3 = pi3d.MergeShape(name="trees3")
mytrees3.cluster(treemodel2, mymap,0.0, 0.0, 300.0, 300.0, 20, "", 4.0, 2.0)
mytrees3.set_draw_details(flatsh, [hb2img], 0.0, 0.0)
mytrees3.set_fog(*TFOG)

#Create monument
monument = pi3d.Model(file_string="models/pi3d.obj", name="monument")
monument.set_shader(shinesh)
monument.set_normal_shine(bumpimg, 16.0, reflimg, 0.4)
monument.set_fog(*FOG)
monument.translate(100.0, -mymap.calcHeight(100.0, 235) + 12.0, 235.0)
monument.scale(20.0, 20.0, 20.0)
monument.rotateToY(65)

#screenshot number
scshots = 1

#avatar camera
rot = 0.0
tilt = 0.0
avhgt = 3.5
xm = 0.0
zm = 0.0
ym = mymap.calcHeight(xm, zm) + avhgt

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()

omx, omy = mymouse.position()

# Display scene and rotate cuboid
while DISPLAY.loop_running():
  CAMERA.move_camera((xm, ym, zm), rot, tilt)
  myecube.position(xm, ym, zm)
  for i in range(2):
    CAMERA.start_capture(i)
    monument.draw()
    mymap.draw()
    if abs(xm) > 300:
      mymap.position(math.copysign(1000,xm), 0.0, 0.0)
      mymap.draw()
    if abs(zm) > 300:
      mymap.position(0.0, 0.0, math.copysign(1000,zm))
      mymap.draw()
      if abs(xm) > 300:
        mymap.position(math.copysign(1000,xm), 0.0, math.copysign(1000,zm))
        mymap.draw()
    mymap.position(0.0, 0.0, 0.0)
    myecube.draw()
    mytrees3.draw()
    mytrees2.draw()
    mytrees1.draw()
    CAMERA.end_capture(i)
  CAMERA.draw()

  mx, my = mymouse.position()
  buttons = mymouse.button_status()

  rot -= (mx-omx)*0.2
  tilt += (my-omy)*0.2
  omx=mx
  omy=my

  #Press ESCAPE to terminate
  k = mykeys.read()
  if k >-1 or buttons > mymouse.BUTTON_UP:
    if k == 119 or buttons == mymouse.LEFT_BUTTON:  #key W
      xm += CAMERA.camera_3d.mtrx[0, 3] 
      zm += CAMERA.camera_3d.mtrx[2, 3]
      ym = mymap.calcHeight(xm, zm) + avhgt
    elif k == 115 or buttons == mymouse.RIGHT_BUTTON:  #kry S
      xm -= CAMERA.camera_3d.mtrx[0, 3] 
      zm -= CAMERA.camera_3d.mtrx[2, 3]
      ym = mymap.calcHeight(xm, zm) + avhgt
    elif k == 112:  #key P
      pi3d.screenshot("forestWalk"+str(scshots)+".jpg")
      scshots += 1
    elif k == 10:   #key RETURN
      mc = 0
    elif k == 27:  #Escape key
      mykeys.close()
      mymouse.stop()
      DISPLAY.stop()
      break

    halfsize = mapsize / 2.0
    xm = (xm + halfsize) % mapsize - halfsize # wrap location to stay on map -500 to +500
    zm = (zm + halfsize) % mapsize - halfsize
