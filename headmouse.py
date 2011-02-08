#! /usr/bin/env python

import time
from Xlib import display
from OSCeleton import OSCeleton, Point


MOVE_POINTER = 2        
        
if __name__ == "__main__":
    server = OSCeleton(7110)
    count = 0
    prev_time = time.time()
    wanted = ['head', 'neck', 'l_shoulder', 'r_shoulder', 'torso']
    xd = display.Display()
    frame_count = 0
    while True:
        server.run()
        if server.frames > frame_count:
            if wanted in server:
                head = server.joints['head']
                neck = server.joints['neck']
                l_shoulder = server.joints['l_shoulder']
                r_shoulder = server.joints['r_shoulder']
                torso = server.joints['torso']
                sh_dist = l_shoulder - r_shoulder
                print count
                hls = head - l_shoulder
                hrs = head - r_shoulder
                hn = head - neck
                ht = head - torso
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
                prev_time = time.time()
                frame_count = server.frames
  
