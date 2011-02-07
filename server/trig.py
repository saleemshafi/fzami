#!/usr/bin/env python

from math import *

#---------------------- Trigonometric Functions -----------------------

def dsin(d):
    return sin(radians(d))

# degree cos
def dcos(d):
    return cos(radians(d))

# degree tan
def dtan(d):
    return tan(radians(d))

# degree arcsin
def darcsin(x):
    return degrees(asin(x))

# degree arccos
def darccos(x):
    return degrees(acos(x))

# degree arctan
def darctan(x):
    return degrees(atan(x))

# degree arccot
def darccot(x):
    return degrees(atan(1.0/x))

# degree arctan2
def darctan2(y, x):
    return degrees(atan2(y, x))

# range reduce angle in degrees.
def fixangle(angle):
	return fix(angle, 360.0)
	
# range reduce hours to 0..23
def fixhour(hour):
	return fix(hour, 24.0)

def fix(a, mode):
	a = a - mode * ( floor( a / mode ) )
	return a + mode if a < 0 else a

