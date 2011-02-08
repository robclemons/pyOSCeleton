#! /usr/bin/env python

from math import sqrt
import liblo

class Point:
    '''Euclidean difference can be found with:
        >>> joint_c = joint_a - joint_b
        >>> joint_c.magnitude()
    '''
    def __init__(self, (x, y, z)):
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        s = "(%f, %f, %f)" % (self.x, self.y, self.z)
        return s
        
    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        else:
            return False
            
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Point((x, y, z))
        
    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Point((x, y, z))
        
    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
            
    def normalize(self):
        mag = self.magnitude()
        self.x = self.x / mag
        self.y = self.y / mag
        self.z = self.z / mag


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
        self.joints[str(args[0])] = Point(args[2:])
        
    def run(self, timeout = 100):
        self.server.recv(timeout)
        
    def __contains__(self, wanted):
        intersection = set(wanted) & set(self.joints)
	return bool(len(intersection))
