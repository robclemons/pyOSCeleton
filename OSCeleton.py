#! /usr/bin/env python

from math import sqrt
import liblo

HEAD = 'head'
NECK = 'neck'
LEFT_COLLAR = 'l_collar'
RIGHT_COLLAR = 'r_collar'
LEFT_SHOULDER = 'l_shoulder'
RIGHT_SHOULDER = 'r_shoulder'
LEFT_ELBOW = 'l_elbow'
RIGHT_ELBOW = 'r_elbow'
LEFT_WRIST = 'l_wrist'
RIGHT_WRIST = 'r_wrist'
LEFT_HAND = 'l_hand'
RIGHT_HAND = 'r_hand'
LEFT_FINGERTIP = 'l_fingertip'
RIGHT_FINGERTIP = 'r_fingertip'
TORSO = 'torso'
LEFT_HIP = 'l_hip'
RIGHT_HIP = 'r_hip'
LEFT_KNEE = 'l_knee'
RIGHT_KNEE = 'r_knee'
LEFT_ANKLE = 'l_ankle'
RIGHT_ANKLE = 'r_ankle'
LEFT_FOOT = 'l_foot'
RIGHT_FOOT = 'r_foot'

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

class Skeleton:
    joints = {}
    
    def __init__(self, user):
        self.id = user
                        
    def __contains__(self, wanted):
        return set(wanted) <= set(self.joints)
        
    def __setitem__(self, key, value):
        self.joints[key] = value
        
    def __getitem__(self, key):
        return self.joints[key]
        
    def clear(self):
        self.joints.clear()

class OSCeleton:
    users = {}
    frames = 0
    lost_user = False
    
    def __init__(self, port = 7110):
        self.server = liblo.Server(port)
        self.server.add_method("/new_user", 'i', self.new_user_callback)
        self.server.add_method("/lost_user", 'i', self.lost_user_callback)
        self.server.add_method("/new_skel", 'i', self.new_skeleton_callback)
        self.server.add_method("/joint", 'sifff', self.joint_callback)
    
    def new_user_callback(self, path, args, types, src):
        print "New user %d" % args[0]
        self.users[args[0]] = Skeleton(args[0])
        
    def lost_user_callback(self, path, args, types, src):
        print "User %d has been lost" % args[0]
        try:
            del self.users[args[0]]
            self.lost_user = True
        except KeyError:
            pass
        
    def new_skeleton_callback(self, path, args, types, src):
        print "Calibration complete, now tracking User %d" % args[0]
        
    def joint_callback(self, path, args, types, src):
        if str(args[0]) == HEAD:
            self.users[args[1]].clear()
            self.frames += 1
        if args[1] not in self.users:
            self.users[args[1]] = Skeleton(args[1])
        self.users[args[1]][str(args[0])] = Point(args[2:])
        
    def get_users(self):
        return self.users.keys()
        
    def get_skeletons(self):
        return self.users.values()
        
    def run(self, timeout = 100):
        self.server.recv(timeout)

