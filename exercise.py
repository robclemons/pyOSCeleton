#! /usr/bin/env python

import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OSCeleton import OSCeleton, Point

SIZE_X = 640
SIZE_Y = 480

server = OSCeleton(7110)
wanted = ['head', 'neck', 'torso', 'l_shoulder', 'l_elbow', 'l_hand', 'l_hip', 'r_shoulder', 'r_elbow', 'r_hand', 'r_hip']
frame_count = 0
joints = {}

def drawLine(joint1, joint2):
    glVertex3f(joint1.x, 1 - joint1.y, joint1.z)
    glVertex3f(joint2.x, 1 - joint2.y, joint2.z)
    
def glutIdle():
    global frame_count, joints
    server.run()
    if server.frames > frame_count and (wanted in server):
        joints = server.joints.copy()
        frame_count = server.frames
        glutPostRedisplay()

def glutDisplay():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glShadeModel(GL_SMOOTH)
    glLoadIdentity()
    if 'head' in joints:
        glBegin(GL_LINES)
        drawLine(joints['head'], joints['neck'])
        drawLine(joints['neck'], joints['torso'])
        drawLine(joints['l_shoulder'], joints['r_shoulder'])
        drawLine(joints['l_shoulder'], joints['l_elbow'])
        drawLine(joints['l_elbow'], joints['l_hand'])   
        drawLine(joints['r_shoulder'], joints['r_elbow'])
        drawLine(joints['r_elbow'], joints['r_hand'])
        drawLine(joints['l_shoulder'], joints['l_hip'])
        drawLine(joints['r_shoulder'], joints['r_hip'])
        drawLine(joints['l_hip'], joints['r_hip'])
        glEnd()
    glFlush()
    glutSwapBuffers()
    
if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(SIZE_X, SIZE_Y)
    glutCreateWindow("Pynectercise")
    glOrtho(0, 1, 0, 1, -7.8125, 7.8125)
    glutDisplayFunc(glutDisplay)
    glutIdleFunc(glutIdle)
    glutMainLoop()

                
