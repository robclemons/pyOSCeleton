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

import sys
import time
from ConfigParser import SafeConfigParser
from collections import deque
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OSCeleton import *

SIZE_X = 640
SIZE_Y = 480
TARGET_SIZE = 60
REMOVE_AFTER = 2
usersTargets = []
server = OSCeleton(7110)
server.realWorld = True
frameCount = 0
users = {}
lastDisplayed = 0.0

class Player(Skeleton):
    """Holds a players data.  Inherits from Skeleton.
    
    Player.hits is a counter for the number of targets this player hits.
    
    Player.last is the time at which this player's joints were updated. 
    """
    
    def __init__(self, user_id):
        Skeleton.__init__(self, user_id)
        self.hits = 0
        self.last = 0.0
        
    def still_moving(self):
        """Tests whether the Player's joints have been updated recently"""
        return time.time() - self.last < REMOVE_AFTER
        
class Target(Point):
    """Stores target information"""
    def __init__(self, x, y, z):
        Point.__init__(self, x, y, z)
        self.baseJoint = ""
        self.middleJoint = ""
        self.hitJoint = ""
        self.calcLen = False
    
def getTargets(iniFile):
    """Parses ini file and adds the targets found in the file to users_targets"""
    global usersTargets
    parser = SafeConfigParser()
    parser.read(iniFile)
    targList = parser.sections()
    targList.sort()
    for section in targList:
        x = parser.getfloat(section, 'x')
        y = parser.getfloat(section, 'y')
        z = parser.getfloat(section, 'z')
        t = Target(x, y, z)
        t.baseJoint = parser.get(section, 'baseJoint')
        t.middleJoint = parser.get(section, 'middleJoint')
        t.hitJoint = parser.get(section, 'hitJoint')
        if parser.has_option(section, 'calcLen'):
            t.calcLen = parser.getboolean(section, 'calcLen')
        usersTargets.append(t)
    
def getRGB(joint, colorRange = 800):
    """Returns a tuple with r, g and b color values based on joint's Z.
    
    Ugly but does the job, needs to be completely rewritten"""
    z = joint.z
    z = z % colorRange #smaller range gives more noticeable transitions
    subInterval = colorRange / 6.0
    rgb = [0, 0, 0]
    if z < subInterval:
        rgb[0] = 1.0
        rgb[1] = z / subInterval
    elif z < 2 * subInterval:
        rgb[1] = 1.0
        rgb[0] = (2 * subInterval - z) / subInterval
    elif z < 3 * subInterval:
        rgb[1] = 1.0
        rgb[2] = (z - 2 * subInterval) / subInterval
    elif z < 4 * subInterval:
        rgb[2] = 1.0
        rgb[1] = (4 * subInterval - z) / subInterval
    elif z < 5 * subInterval:
        rgb[2] = 1.0
        rgb[0] = (z - 4 * subInterval) / subInterval
    else:
        rgb[0] = 1
        rgb[2] = (colorRange - z) / subInterval
    return tuple(rgb)

def drawLine(player, jointLabel1, jointLabel2):
    """Accepts a skeleton and two joint labels.
    
    Draws a colored line between the skeleton's two joints that have the desired labels"""
    if (jointLabel1, jointLabel2) in player:
        joint1 = player[jointLabel1]
        joint2 = player[jointLabel2]
        r, g, b = getRGB(joint1)
        glColor3f(r, g, b)
        glVertex3f(joint1.x, joint1.y, joint1.z)
        r, g, b = getRGB(joint2)
        glColor3f(r, g, b)
        glVertex3f(joint2.x, joint2.y, joint2.z)
            
def glutIdle():
    """Registered as GlutIdleFunc.
    
    Catches server events, adds and removes users and loads newest Skeletons"""
    global frameCount, users
    server.run()
    if server.frames > frameCount or server.lostUsers:
        if server.lostUsers:
            try:
                for each in server.lostUsers:
                    del users[each]
                    glutPostRedisplay()
            except KeyError:
                pass
            del server.lostUsers[:]
        for player in server.get_new_skeletons():
            if player.id not in users:
                users[player.id] = Player(player.id)
            users[player.id].joints = player.copy_joints()
            users[player.id].last = time.time()
            frameCount = server.frames
            glutPostRedisplay()
    elif time.time() - lastDisplayed > REMOVE_AFTER:
        glutPostRedisplay()
        
def drawPlayers():
    """Draws lines connecting available joints for every player in users"""
    glBegin(GL_LINES)
    for player in users.values():
        if player.still_moving():
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
    glMatrixMode(GL_MODELVIEW)
    glLineWidth(1)
    for player in users.values():
        if player.still_moving():
            targ = usersTargets[player.hits % len(usersTargets)]
            if (targ.baseJoint, targ.middleJoint, targ.hitJoint) in player:
                orientation = getPlayersOrientation(player)
                #draws a sphere on the joint the player has to use
                glPushMatrix()
                ball = player[targ.hitJoint]
                glTranslate(ball.x, ball.y, ball.z)
                glColor3f(1, 1, 1)
                glutSolidSphere(TARGET_SIZE/ 2.0, 30, 30)
                glPopMatrix()
                glPushMatrix()
                #rotates target along the y axis, ie user turns side to side
                yRotMat = np.array([[np.cos(orientation.x * -np.pi/2.0), 0, -np.sin(orientation.x * -np.pi/2.0)],
                          [0, 1, 0],
                          [np.sin(orientation.x * -np.pi/2.0), 0, np.cos(orientation.x * -np.pi/2.0)]])
                #rotates target along the x axis, ie user leans forward or back
                xRotMat = np.array([[1, 0, 0],
                          [0, np.cos(orientation.y * np.pi/2.0), np.sin(orientation.y * np.pi/2.0)],
                          [0, -np.sin(orientation.y * np.pi/2.0), np.cos(orientation.y * np.pi/2.0)]])
                #determines target position based on limb length
                if targ.calcLen:
                    mag = (player[targ.middleJoint] - player[targ.baseJoint]).magnitude()
                    mag += (player[targ.hitJoint] - player[targ.middleJoint]).magnitude()
                    targ.normalize()
                    targList = [targ.x * mag,  targ.y * mag, targ.z * mag]
                else:
                    targList = targ.vals()
                targList = np.dot(yRotMat, targList)
                targList = np.dot(xRotMat, targList)
                targPoint = Point(targList[0], targList[1], targList[2])
                targPoint += player[targ.baseJoint]
                glTranslate(targPoint.x, targPoint.y, targPoint.z)
                #target is hit if hit_joint is inside target
                ht = player[targ.hitJoint] - targPoint
                if abs(ht.x) < TARGET_SIZE and abs(ht.y) < TARGET_SIZE and abs(ht.z) < TARGET_SIZE:
                    r, g, b = (1, 1, 1)
                    player.hits += 1
                else:
                    r, g, b = getRGB(targPoint)
                glRotatef(orientation.x * 90, 0, 1, 0)
                glRotatef(orientation.y * -90, 1, 0, 0)
                glColor3f(r, g, b)
                glutSolidCube(TARGET_SIZE)
                glColor3f(0, 0, 0)
                glutWireCube(TARGET_SIZE + 1)
                glPopMatrix()        
    
def getPlayersOrientation(player):
    """Determines a users orientation.
    
    Accepts a Skeleton and returns a Point.
    
    Calculates orientation by using 3 points to create two vectors
    and then cross multiplies those vectors to find a vector perpindicular to both"""
    if (TORSO, LEFT_SHOULDER, RIGHT_SHOULDER) in player:
        torso = player[TORSO]
        tl = player[LEFT_SHOULDER] - player[TORSO]
        tr = player[RIGHT_SHOULDER] - player[TORSO]
        tl.normalize()
        tr.normalize()
        orientationArray = np.cross(tr.vals(), tl.vals())
        orientation = Point(orientationArray[0], orientationArray[1], orientationArray[2]) 
        orientation.normalize()
    else:
        orientation = Point(1, 1, 1)
        orientation.normalize()
    return orientation
    
def glutDisplay():
    """Registered as GlutDisplayFunc.  Calls all drawing functions"""
    global last_displayed
    lastDisplayed = time.time()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glShadeModel(GL_SMOOTH)
    glLineWidth(5)
    glLoadIdentity()
    drawPlayers()
    drawTarget()
    glFlush()
    glutSwapBuffers()
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        iniFile = sys.argv[1]
    else:
        iniFile = "generic.ini"
    getTargets(iniFile)
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

