#! /usr/bin/env python

"""
   Written by: Robbie Clemons
   Email: RobClemons@gmail.com
   File: exercise.py
   Licensed under GNU GPLv3
   Released February 2011

   exercise.py demonstrates using pyOSCeleton to draw users' skeletons
   and allow the users to hit targets.  For proper results use the -r option
   when you start OSCeleton to disable mirror mode.  I got the best results when using the noise filter(-f option).
"""

# Copyright (C) 2011 Robbie Clemons
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OSCeleton import *

SIZE_X = 640
SIZE_Y = 480
TARGET_SIZE = 60
TARGET = [Point(1, 1, -440), Point(-440, 0, 50), Point(0, -440, 50)]

server = OSCeleton(7110)
server.real_world = True
frame_count = 0
users = {}
hits = 0
orientation = Point(0,0,0)

def cross(p1, p2):
    """Determines the cross product of two vectors"""
    x = p1.y * p2.z - p1.z * p2.y
    y = p1.z * p2.x - p1.x * p2.z
    z = p1.x * p2.y - p1.y * p2.x
    return Point(x, y, z)
    
def getRGB(joint, color_range = 600):
    """Returns a tuple with r, g and b color values based on joint's Z.
    
    Ugly but does the job, needs to be completely rewritten"""
    z = joint.z
    z = z % color_range #smaller range gives more noticeable transitions
    sub_interval = color_range / 6.0
    rgb = [0, 0, 0]
    if z < sub_interval:
        rgb[0] = 1.0
        rgb[1] = z / sub_interval
    elif z < 2 * sub_interval:
        rgb[1] = 1.0
        rgb[0] = (2 * sub_interval - z) / sub_interval
    elif z < 3 * sub_interval:
        rgb[1] = 1.0
        rgb[2] = (z - 2 * sub_interval) / sub_interval
    elif z < 4 * sub_interval:
        rgb[2] = 1.0
        rgb[1] = (4 * sub_interval - z) / sub_interval
    elif z < 5 * sub_interval:
        rgb[2] = 1.0
        rgb[0] = (z - 4 * sub_interval) / sub_interval
    else:
        rgb[0] = 1
        rgb[2] = (color_range - z) / sub_interval
    return tuple(rgb)

def drawLine(player, joint_label1, joint_label2):
    """Accepts a skeleton and two joint labels.
    
    Draws a colored line between the skeleton's two joints that have the desired labels"""
    if (joint_label1, joint_label2) in player:
        joint1 = player[joint_label1]
        joint2 = player[joint_label2]
        r, g, b = getRGB(joint1)
        glColor3f(r, g, b)
        glVertex3f(joint1.x, joint1.y, joint1.z)
        r, g, b = getRGB(joint2)
        glColor3f(r, g, b)
        glVertex3f(joint2.x, joint2.y, joint2.z)
            
def glutIdle():
    """Registered as GlutIdleFunc.
    
    Catches server events, adds and removes users and loads newest Skeletons"""
    global frame_count, users
    server.run()
    if server.frames > frame_count or server.lost_user:
        lost_users = set(users.keys()) - set(server.get_users())
        for each in lost_users:
            del users[each]
            glutPostRedisplay()
        server.lost_user = False
        for player in server.get_skeletons():
             users[player.id] = player
             frame_count = server.frames
             glutPostRedisplay()
                
def drawPlayers():
    """Draws lines connecting available joints for every player in users"""
    glBegin(GL_LINES)
    for player in users.values():
        drawLine(player, HEAD, NECK)
        drawLine(player, NECK, TORSO)
        drawLine(player, LEFT_SHOULDER, LEFT_HIP)
        drawLine(player, RIGHT_SHOULDER, RIGHT_HIP)
        drawLine(player, LEFT_HIP, RIGHT_HIP)
        drawLine(player, LEFT_HIP, LEFT_KNEE)
        drawLine(player, LEFT_KNEE, LEFT_FOOT)
        drawLine(player, RIGHT_HIP, RIGHT_KNEE)
        drawLine(player, RIGHT_KNEE, RIGHT_FOOT)
        drawLine(player, LEFT_SHOULDER, RIGHT_SHOULDER)
        drawLine(player, LEFT_SHOULDER, LEFT_ELBOW)
        drawLine(player, LEFT_ELBOW, LEFT_HAND)   
        drawLine(player, RIGHT_SHOULDER, RIGHT_ELBOW)
        drawLine(player, RIGHT_ELBOW, RIGHT_HAND)
    glEnd()
    
def drawTarget():
    """Draw a target changing its' position each time it's hit"""
    global hits
    glMatrixMode(GL_MODELVIEW)
    glLineWidth(1)
    for player in users.values():
        if (RIGHT_SHOULDER, RIGHT_HAND) in player:
            glPushMatrix()
            joint = player[RIGHT_SHOULDER]
            armLen = 440
            target = Point(orientation.x * armLen , orientation.y * armLen, orientation.z * armLen)
            target += player[RIGHT_SHOULDER]
            glTranslate(target.x, target.y, target.z)
            ht = player[RIGHT_HAND] - target
            if abs(ht.x) < TARGET_SIZE and abs(ht.y) < TARGET_SIZE and abs(ht.z) < TARGET_SIZE:
                r, g, b = (1, 1, 1)
                hits += 1
            else:
                r, g, b = getRGB(target)
            glRotatef(orientation.x * 90, 0, 1, 0)
            glRotatef(orientation.y * -90, 1, 0, 0)
            glColor3f(r, g, b)
            glutSolidCube(TARGET_SIZE)
            glColor3f(0, 0, 0)
            glutWireCube(TARGET_SIZE + 1)
            glPopMatrix()        
    
def drawPlayersOrientation():
    """Determines and draws a users orientation.
    
    Calculates orientation by using 3 points to create two vectors
    and then cross multiplies those vectors to find a vector perpindicular to both"""
    global orientation
    glBegin(GL_LINES)
    for player in users.values():
        if (TORSO, LEFT_SHOULDER, RIGHT_SHOULDER) in player:
            torso = player[TORSO]
            l_shoulder = player[LEFT_SHOULDER]
            tl = player[LEFT_SHOULDER] - player[TORSO]
            tr = player[RIGHT_SHOULDER] - player[TORSO]
            tl.normalize()
            tr.normalize()
            orientation = cross(tr, tl)
            orientation.normalize()
            r, g, b = getRGB(torso)
            glColor3f(r, g, b)
            glVertex3f(torso.x, torso.y, torso.z)
            orient_line = torso + orientation
            r, g, b = getRGB(orient_line)
            glColor3f(r, g, b)
            glVertex3f(orient_line.x, orient_line.y, orient_line.z)
    glEnd()
    
    
def glutDisplay():
    """Registered as GlutDisplayFunc.  Calls all drawing functions"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glShadeModel(GL_SMOOTH)
    glLineWidth(5)
    glLoadIdentity()
    drawPlayers()
    drawPlayersOrientation()
    drawTarget()
    glFlush()
    glutSwapBuffers()
    
if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(SIZE_X, SIZE_Y)
    glutCreateWindow("PyExercise")
    glOrtho(-1280, 1280, -960, 960, 0, 10000)
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(glutDisplay)
    glutIdleFunc(glutIdle)
    glLineWidth(5)
    glutMainLoop()

                
