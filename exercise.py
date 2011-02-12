#! /usr/bin/env python

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OSCeleton import *

SIZE_X = 640
SIZE_Y = 480
TARGET_SIZE = 0.01

server = OSCeleton(7110)
frame_count = 0
users = {}
    
def getRGB(joint):
    z = joint.z * 3
    z = z % 3 #smaller total gives more noticeable transitions
    rgb = [0, 0, 0]
    if z < 0.5:
        rgb[0] = 1.0
        rgb[1] = z / 0.5
    elif z < 1.0:
        rgb[1] = 1.0
        rgb[0] = (1.0 - z) / 0.5
    elif z < 1.5:
        rgb[1] = 1.0
        rgb[2] = (z - 1.0) / 0.5
    elif z < 2.0:
        rgb[2] = 1.0
        rgb[1] = (2.0 - z) / 0.5
    elif z < 2.5:
        rgb[2] = 1.0
        rgb[0] = (z - 2.0) / 0.5
    else:
        rgb[0] = 1
        rgb[2] = (3.0 - z) / 0.5
    return tuple(rgb)

def drawLine(player, joint_label1, joint_label2):
    if [joint_label1, joint_label2] in player:
        joint1 = player[joint_label1]
        joint2 = player[joint_label2]
        r, g, b = getRGB(joint1)
        glColor3f(r, g, b)
        glVertex3f(joint1.x, 1 - joint1.y, joint1.z)
        r, g, b = getRGB(joint2)
        glColor3f(r, g, b)
        glVertex3f(joint2.x, 1 - joint2.y, joint2.z)
        
def glutIdle():
    global frame_count, users
    server.run()
    if server.frames > frame_count or server.lost_user:
        lost_users = set(users.keys()) - set(server.get_users())
        for each in lost_users:
            del users[each]
            glutPostRedisplay()
        server.lost_user = False
        for player in server.get_skeletons():
#            if wanted in player:
             users[player.id] = player
             frame_count = server.frames
             glutPostRedisplay()
                
def drawPlayers():
    glBegin(GL_LINES)
    for player in users.values():
        drawLine(player, HEAD, NECK)
        drawLine(player, NECK, TORSO)
        drawLine(player, LEFT_SHOULDER, RIGHT_SHOULDER)
        drawLine(player, LEFT_SHOULDER, LEFT_ELBOW)
        drawLine(player, LEFT_ELBOW, LEFT_HAND)   
        drawLine(player, RIGHT_SHOULDER, RIGHT_ELBOW)
        drawLine(player, RIGHT_ELBOW, RIGHT_HAND)
        drawLine(player, LEFT_SHOULDER, LEFT_HIP)
        drawLine(player, RIGHT_SHOULDER, RIGHT_HIP)
        drawLine(player, LEFT_HIP, RIGHT_HIP)
    glEnd()
    
def drawTarget():
    glBegin(GL_QUADS)
    for player in users.values():
        if [LEFT_SHOULDER, LEFT_HAND] in player:
            target = player[LEFT_SHOULDER]
            target.z -= 0.35
            ht = player[LEFT_HAND] - target
            if abs(ht.x) < 0.05 and abs(ht.y) < 0.05 and ht.z < 0:
                r, g, b = (1, 1, 1)
            else:
                r, g, b = getRGB(target)
            glColor3f(r, g, b)
            glVertex3f(target.x - TARGET_SIZE, target.y + TARGET_SIZE, target.z)
            glVertex3f(target.x + TARGET_SIZE, target.y + TARGET_SIZE, target.z)
            glVertex3f(target.x + TARGET_SIZE, target.y - TARGET_SIZE, target.z)
            glVertex3f(target.x - TARGET_SIZE, target.y - TARGET_SIZE, target.z)
    glEnd()
    
def glutDisplay():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glShadeModel(GL_SMOOTH)
    glLoadIdentity()
    drawPlayers()
    drawTarget()
    glFlush()
    glutSwapBuffers()
    
if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(SIZE_X, SIZE_Y)
    glutCreateWindow("PyExercise")
    glOrtho(0, 1, 0, 1, -7.8125, 0)
    glutDisplayFunc(glutDisplay)
    glutIdleFunc(glutIdle)
    glutMainLoop()

                
