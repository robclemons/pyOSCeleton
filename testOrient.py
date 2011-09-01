#! /usr/bin/env python

from OSCeleton import *


framecount = 0
server = OSCeleton()
while True:
    server.run()
    if server.frames > framecount:
        for each in server.get_new_skeletons():
            for jointName, orient in each.orient.items():
                print "joint = " + jointName
                print "orientation = " + str(orient)
