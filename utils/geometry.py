from sympy.geometry.line import Ray, Segment
from sympy.geometry.point import Point
from math import sin

"""
Geometry Helper functions
"""

EPSILON_MULTIPLIER = 0.000001 # 1e-6

def vertexDistance(v1, v2):
	return v1.loc.distance(v2.loc)

def createSegmentFromVertices(v1, v2):
	return Segment(v1.loc, v2.loc)

def createPolygonFromVertices(verts):
	return Segment([v.loc for v in verts])

def getEpsilonVector(v1, v2):
	"""
	Returns a Point which represents an epsilon vector
	"""
	v = v1.loc - v2.loc
	return v * EPSILON_MULTIPLIER

def cross(p1, p2):
	"""
	p1: sympy.geometry.points.Point

	p2: sympy.geometry.points.Point
	"""
	origin = Point(0, 0)
	l1 = p1.distance(origin)
	l2 = p2.distance(origin)
	r1 = Ray(origin, p1)
	r2 = Ray(origin, p2)
	angle = r1.angle_between(r2)
	return l1 * l2 * sin(angle)
