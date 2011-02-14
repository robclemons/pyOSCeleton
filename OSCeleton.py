#! /usr/bin/env python

"""
   Written by: Robbie Clemons
   Email: RobClemons@gmail.com
   Project: pyOSCeleton
   Licensed under GNU GPLv3
   Released February 2011

   This document provides the Point, Skeleton, and OSCeleton classes which
   are meant to recieve and contain skeleton data from OSCeleton.
   
"""

# Copyright (C) 2011 Robbie Clemons
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

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
    """Holds a 3 dimensional point.
    
    Point has 3 properties which are the coordinates x, y and z.
    
    """
    
    def __init__(self, (x, y, z)):
        """Initialize Point object.
        
        Requires a tuple containing the x, y and z coordinates in that order.
        
        """
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        """Return a string in the format (x, y, z)"""
        s = "(%f, %f, %f)" % (self.x, self.y, self.z)
        return s
        
    def __eq__(self, other):
        """Test whether two Points' x, y and z coordinates are equal"""
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        else:
            return False
            
    def __add__(self, other):
        """Add Point objects' coordinates together"""
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Point((x, y, z))
        
    def __sub__(self, other):
        """Subtract Point objects' coordinates"""
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Point((x, y, z))
        
    def magnitude(self):
        """Calculate vector magnitude of Point"""
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
            
    def normalize(self):
        """Normalize Point's x, y and z coordinates"""
        mag = self.magnitude()
        self.x = self.x / mag
        self.y = self.y / mag
        self.z = self.z / mag

#mostly useless class, it's only purpose is overloading __contains__ 
class Skeleton:
    """Holds a user's joint positions
    
    Skeleton.joints is a dictionary whose keys are joint labels
    and its' values are the joint's Point.
    
    Skeleton.id is the user's number
    
    """
    
    joints = {}
    
    def __init__(self, user):
        """Initialize Skeleton.
        
        Requires the user's number
        
        """
        self.id = user
                        
    def __contains__(self, wanted):
        """Test whether Skeleton.joints contains everything passed to it.
        
        Usage:
        
        >>>if [HEAD, NECK] in skeleton:
        >>>    print "skeleton contains HEAD and NECK"
        
        """
        return set(wanted) <= set(self.joints)
        
    def __setitem__(self, key, value):
        self.joints[key] = value
        
    def __getitem__(self, key):
        return self.joints[key]
        
    def clear(self):
        self.joints.clear()

class OSCeleton:
    """Starts a liblo.Server instance and processes each event the server receives.
    
    OSCeleton.server is a liblo.Server instance.
    
    OSCeleton.users is a dictionary whose keys are user ids and
    its' values are Skeleton objects.
    
    OSCeleton.frames is a counter that is incremented every time all of a user's
    recognized joints have been received by the server.
    
    OSCeleton.lost_user is a flag that is set to True whenever the server
    receives a message claiming that the user is no longer seen.
    
    """
    
    users = {}
    _users = {}
    frames = 0
    lost_user = False
    real_world = False
    
    def __init__(self, port = 7110):
        """Initialize OSCeleton.
        
        Accepts the optional argument of the port for the server to listen on.
        
        Creates the server and registers the callbacks.
        
        """
        self.server = liblo.Server(port)
        self.server.add_method("/new_user", 'i', self.new_user_callback)
        self.server.add_method("/lost_user", 'i', self.lost_user_callback)
        self.server.add_method("/new_skel", 'i', self.new_skeleton_callback)
        self.server.add_method("/joint", 'sifff', self.joint_callback)
    
    def new_user_callback(self, path, args, types, src):
        """Create user"""
        print "New user %d" % args[0]
        self._users[args[0]] = Skeleton(args[0])
        
    def lost_user_callback(self, path, args, types, src):
        """Remove user"""
        print "User %d has been lost" % args[0]
        try:
            del self.users[args[0]]
            del self._users[args[0]]
            self.lost_user = True
        except KeyError:
            pass
        
    def new_skeleton_callback(self, path, args, types, src):
        print "Calibration complete, now tracking User %d" % args[0]
        
    def joint_callback(self, path, args, types, src):
        """Add joint to a users skeleton"""
        #add new user if they haven't been added already
        if args[1] not in self._users:
            self._users[args[1]] = Skeleton(args[1])
        #start a new frame and save the old one in users if we already have joint
        if str(args[0]) in self._users[args[1]].joints:
            self.users[args[1]] = self._users[args[1]]
            self._users[args[1]].clear()
            self.frames += 1
        #convert to mm in real world measurements
        if self.real_world:
            x = 1280 - args[2] * 2560
            y = 960 - args[3] * 1920
            z = args[4] * 1280
            self._users[args[1]][str(args[0])] = Point((x,y,z))
        else:
            self._users[args[1]][str(args[0])] = Point(args[2:])
        
    def get_users(self):
        """Return a list of users"""
        return self.users.keys()
        
    def get_skeletons(self):
        """Return a list of skeletons"""
        return self.users.values()
        
    def run(self, timeout = 100):
        """Wait for and catch event.
        
        Accepts optional timeout argument.
        
        """
        self.server.recv(timeout)

