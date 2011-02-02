#! /usr/bin/env python

import liblo

class OSCeleton:
    joints = {}
    user = -1
    frames = 0
    
    def __init__(self, port = 7110):
        self.server = liblo.Server(port)
        self.server.add_method("/new_user", 'i', self.new_user_callback)
        self.server.add_method("/lost_user", 'i', self.lost_user_callback)
        self.server.add_method("/new_skel", 'i', self.new_skeleton_callback)
        self.server.add_method("/joint", 'sifff', self.joint_callback)
    
    def new_user_callback(self, path, args, types, src):
        print "New user %d" % args[0]
        self.user = args[0]
        
    def lost_user_callback(self, path, args, types, src):
        print "User %d has been lost" % args[0]
        self.user = -1
        
    def new_skeleton_callback(self, path, args, types, src):
        print "Calibration complete, now tracking User %d" % args[0]
        
    def joint_callback(self, path, args, types, src):
        if str(args[0]) == "head":
            self.joints.clear()
            self.frames += 1
        self.joints[str(args[0])] = args[2:]
        
    def run(self, timeout = 100):
        self.server.recv(timeout)
        
    def contains(self, wanted):
        for item in wanted:
            if item not in self.joints:
                return False
        return True
