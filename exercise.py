#! /usr/bin/env python

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OSCeleton import *

SIZE_X = 640
SIZE_Y = 480

server = OSCeleton(7110)
wanted = [HEAD, NECK, TORSO, LEFT_SHOULDER, LEFT_ELBOW, LEFT_HAND, LEFT_HIP, RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_HAND, RIGHT_HIP]
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

def drawLine(joint1, joint2):
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
            if wanted in player:
                users[player.id] = player
                frame_count = server.frames
                glutPostRedisplay()

def glutDisplay():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glShadeModel(GL_SMOOTH)
    glLoadIdentity()
    glBegin(GL_LINES)
    for player in users.values():
        drawLine(player[HEAD], player[NECK])
        drawLine(player[NECK], player[TORSO])
        drawLine(player[LEFT_SHOULDER], player[RIGHT_SHOULDER])
        drawLine(player[LEFT_SHOULDER], player[LEFT_ELBOW])
        drawLine(player[LEFT_ELBOW], player[LEFT_HAND])   
        drawLine(player[RIGHT_SHOULDER], player[RIGHT_ELBOW])
        drawLine(player[RIGHT_ELBOW], player[RIGHT_HAND])
        drawLine(player[LEFT_SHOULDER], player[LEFT_HIP])
        drawLine(player[RIGHT_SHOULDER], player[RIGHT_HIP])
        drawLine(player[LEFT_HIP], player[RIGHT_HIP])
    glEnd()
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

                
