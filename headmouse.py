#! /usr/bin/env python

from Xlib import display
from OSCeleton import *


MOVE_POINTER = 2        
        
if __name__ == "__main__":
    server = OSCeleton(7110)
    count = 0
    wanted = [HEAD, NECK, LEFT_SHOULDER, RIGHT_SHOULDER, TORSO]
    xd = display.Display()
    frame_count = 0
    while True:
        server.run()
        if server.frames > frame_count:
            user = server.get_skeletons()[0]
            if wanted in user:
                sh_dist = user[LEFT_SHOULDER] - user[RIGHT_SHOULDER]
                print count
                hls = user[HEAD] - user[LEFT_SHOULDER]
                hrs = user[HEAD] - user[RIGHT_SHOULDER]
                hn = user[HEAD] - user[NECK]
                ht = user[HEAD] - user[TORSO]
                center_offset = 0.0025
                if abs(hrs.x) + center_offset < abs(hls.x):
                    print "R"
                    xd.warp_pointer(MOVE_POINTER,0)
                elif abs(hls.x) + center_offset < abs(hrs.x):
                    print "L"
                    xd.warp_pointer(-MOVE_POINTER,0)
                else:
                    print "C"
                if ht.z < 0.045:
                    print "D"
                    xd.warp_pointer(0, MOVE_POINTER)
                elif ht.z > 0.065:
                    print "U"
                    xd.warp_pointer(0, -MOVE_POINTER)
                else:
                    print "M"
                print "distance between SHOULDER = %f" % sh_dist.magnitude()
                print "HEAD - L_SHOULDER = " + str(hls)
                print "HEAD - R_SHOULDER = " + str(hrs)
                print "HEAD - NECK = " + str(hn)
                print "HEAD - TORSO = " + str(ht)
                xd.flush()
                count += 1
                frame_count = server.frames
  
