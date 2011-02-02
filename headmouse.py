#! /usr/bin/env python

from math import sqrt
import time
from OSCeleton import OSCeleton

class Coord:
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
        return Coord((x, y, z))
        
    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Coord((x, y, z))
        
    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
            
    def normalize(self):
        mag = self.magnitude()
        self.x = self.x / mag
        self.y = self.y / mag
        self.z = self.z / mag
        
        
if __name__ == "__main__":
    server = OSCeleton(7110)
    count = 0
    prev_time = time.time()
    wanted = ['head', 'neck', 'l_shoulder', 'r_shoulder', 'torso']
    while True:
        server.run()
        if (time.time() - prev_time) > 3:
            if server.contains(wanted):
                head = Coord(server.joints['head'])
                neck = Coord(server.joints['neck'])
                l_shoulder = Coord(server.joints['l_shoulder'])
                r_shoulder = Coord(server.joints['r_shoulder'])
                torso = Coord(server.joints['torso'])
                sh_dist = l_shoulder - r_shoulder
                print count
                hls = head - l_shoulder
                hrs = head - r_shoulder
                hn = head - neck
                ht = head - torso
                center_offset = 0.0025
                if abs(hrs.x) + center_offset < abs(hls.x):
                    print "R"
                elif abs(hls.x) + center_offset < abs(hrs.x):
                    print "L"
                else:
                    print "C"
                if ht.z < 0.045:
                    print "D"
                elif ht.z > 0.065:
                    print "U"
                else:
                    print "M"
                print "distance between SHOULDER = %f" % sh_dist.magnitude()
                print "HEAD - L_SHOULDER = " + str(head - l_shoulder)
                print "HEAD - R_SHOULDER = " + str(head - r_shoulder)
                print "HEAD - NECK = " + str(head - neck)
                print "HEAD - TORSO = " + str(head - torso)
                count += 1
                prev_time = time.time()
  
