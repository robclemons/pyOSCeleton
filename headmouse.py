#! /usr/bin/env python

import liblo
from math import sqrt
import time
import numpy as np
class SkeletonServer:
    joints = {}
    user = 0
    skeleton = 0
    wanted = ['head', 'neck', 'l_shoulder', 'r_shoulder', 'torso']
    snapshots = []
    ititial = {}
    def __init__(self, port = 7110):
        self.port = port
        self.server = liblo.Server(7110)
        self.server.add_method("/new_user", 'i', self.new_user_callback)
        self.server.add_method("/lost_user", 'i', self.lost_user_callback)
        self.server.add_method("/new_skel", 'i', self.new_skeleton_callback)
        self.server.add_method("/joint", 'sifff', self.joint_callback)
        
    def new_user_callback(self, path, args, types, src):
        print "New user detected"
        print "Waiting for Psi(muscle man) pose"
        self.user = args[0]
        
    def lost_user_callback(self, path, args, types, src):
        print "User %d has been lost" % args[0]
        self.user = 0
        
    def new_skeleton_callback(self, path, args, types, src):
        print "It's a Skeleton!"
        print "Track him! don't let him get away"
        self.skeleton = args[0]
        
    def joint_callback(self, path, args, types, src):
        if str(args[0]) == "head":
            self.joints.clear()
        self.joints[str(args[0])] = args[2:]
            
    def run(self):
        self.server.recv(100)
        
    def print_joints(self):
        items = self.joints.items()
        for each in items:
            print str(each[0]) + ':' + str(each[1])
            
    def print_differences(self):
        skel_count = len(self.snapshots)
        if skel_count >= 2:
            old_skel = self.snapshots[skel_count - 2]
            new_skel = self.snapshots[skel_count - 1]
            for each in self.wanted:
                newx, newy, newz = new_skel.get(each)
                oldx, oldy, oldz = old_skel.get(each)
                print "%s %f, %f, %f : " % (each, newx - oldx, newy - oldy, newz - oldz),
        else:
            print 'first snapshot'
        print
        
    def get_difference(self, joint_name, old_vals):
        newx, newy, newz = self.joints[joint_name]
        oldx, oldy, oldz = old_vals
        return newx - oldx, newy - oldy, newz - oldz
        
    def print_relative(self, relative_joints):
        root = relative_joints.pop(0)
        rx, ry, rz = self.joints[root]
        for item in relative_joints:                    
            ix, iy, iz = self.joints[item]
            print "%s - %s = %f, %f, %f  :  " % (root, item, rx-ix, ry-iy, rz-iz)
            
    def magnitude(self, (x, y, z)):
        return sqrt(x ** 2 + y ** 2 + z ** 2)
            
    def normalize(self, (x,y,z)):
        mag = self.magnitude((x,y,z))
        return (x / mag, y / mag, z / mag)
        
    def euclidean_distance(self, point1, point2):
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            
if __name__ == "__main__":
    skel_server = SkeletonServer(7110)
    count = 0
    old_head = []
    clock_time = time.time()
    print "sit straight up for initialization"
    while True:
        skel_server.run()
        if (time.time() - clock_time) > 3:
            ready = True
            # check that we have all the points we need
            for joint in skel_server.wanted:
                if joint not in skel_server.joints:
                    ready = False
            if ready:
                head = skel_server.joints['head']
                r_shoulder = skel_server.joints['r_shoulder']
                l_shoulder = skel_server.joints['l_shoulder']
                head[2] = 0.0
                r_shoulder[2] = 0.0
                l_shoulder[2] = 0.0
                l_dist = np.subtract(head, l_shoulder)
                r_dist = np.subtract(head, r_shoulder)
                left = skel_server.euclidean_distance(head, l_shoulder)
                right = skel_server.euclidean_distance(head, r_shoulder)
                n_head = skel_server.normalize(head)
                n_l_shoulder = skel_server.normalize(l_shoulder)
                n_r_shoulder = skel_server.normalize(r_shoulder)
                n_left = skel_server.euclidean_distance(n_head, n_l_shoulder)
                n_right = skel_server.euclidean_distance(n_head, n_r_shoulder)
#                print "left mag = %f; right mag = %f;" % (l_mag, r_mag)
                shift = left - right
                n_shift = n_left - n_right
                print "left eu dist = %f; right eu dist = %f; shift = %f" % (left, right, shift)
                print "n_left dist = %f; n_right dist = %f; n_shift = %f" % (n_left, n_right, n_shift)
                if shift >= -0.5:
                    print "head tilted LEFT"
                elif shift <= -1.0:
                    print "head tilted RIGHT"
                else:
                    print "head is STRAIGHT"
                if count % 3 == 0:
                    print "hold head up straight"
                elif count % 3 == 1:
                    print "tilt head left"
                else:
                    print "tilt head right"

                clock_time = time.time()
                count += 1
      
