import numpy as np
from utils.cgal.types import Line, Point, Polygon, Vector, convertToPoint, crossProduct
from math import sqrt

from model.modelService import Model

"""
Geometry Helper functions
"""
model = Model()
EPSILON_MULTIPLIER = 0.000001 # 1e-6

def vertexDistance(v1, v2):
	pt1 = convertToPoint(v1)
	pt2 = convertToPoint(v2)
	vec = pt1 - pt2
	return sqrt(vec.squared_length())

def getEpsilonVector(frm, to) -> Vector:
	"""
	Returns a Vector which represents an epsilon vector
	"""
	toPt = convertToPoint(to)
	frmPt = convertToPoint(frm)
	vec = toPt - frmPt
	return vec * EPSILON_MULTIPLIER

def isInsidePoly(poly, pt):
	"""
	Check if point `pt` is inside Polygon `poly`
	"""
	if isinstance(pt, Point):
		return poly.has_on_bounded_side(pt)
	else:
		return poly.has_on_bounded_side(pt.loc)

def getAllIntersectingObstacles(vertices):
	"""
	Given the vertices of a polygon, get all the Obstacles that fall intersect (fully or partially) the polygon

	Params
	===
	vertices: `Vertex[]`

	:returns: A tuple of two arrays, First array are fully inside, second array is partially inside
	"""
	result = ([], [])
	poly = Polygon()
	for vert in vertices:
		poly.push_back(vert.loc)
	for obs in model.obstacles:
		isIn = False
		isOut = False
		for pt in obs.vertices:
			if isInsidePoly(poly, pt):
				isIn = True
			else:
				isOut = True
		if isIn:
			if not isOut:
				result[0].append(obs)
			else:
				result[1].append(obs)
	return result

def isColinear(ref1, ref2, target) -> bool:
	"""
	Given the two reference points, determine if target is colinear with line segment formed by ref1->ref2
	"""
	pt1 = convertToPoint(ref1)
	pt2 = convertToPoint(ref2)
	ptTarget = convertToPoint(target)

	line = Line(pt1, pt2)
	return line.has_on(ptTarget)

def isToTheRight(ref1, ref2, target) -> bool:
	"""
	Given the two reference points, determine if target is to the Right of the line segment formed by ref1->ref2
	"""
	pt1 = convertToPoint(ref1)
	pt2 = convertToPoint(ref2)
	ptTarget = convertToPoint(target)

	vec1 = pt2 - pt1
	vec2 = ptTarget - pt1
	cVec3D = crossProduct(vec1, vec2)
	# NOTE: In a standard coordinate system, negative indicates being to the right (right-hand rule: https://en.wikipedia.org/wiki/Right-hand_rule)
	# BUTT in our system (the TkInter Canvas), origin is the top left of the screen and y increases the lower a point is
	# return cVec3D.z() < 0
	return cVec3D.z() > 0

def midpoint(vrt1, vrt2) -> Point:
	pt1 = convertToPoint(vrt1)
	pt2 = convertToPoint(vrt2)
	vec = pt2 - pt1
	return pt1 + (vec / 2)

def lengthOfCurve(pts: list):
	"""
	Takes a curve as a list of points and calculates the total length
	"""
	l = 0
	for i in range(len(pts) - 1):
		l += vertexDistance(pts[i], pts[i + 1])
	return l

def centroid(pts):
	arr = [convertToPoint(pt) for pt in pts]
	cx = np.mean([pt.x() for pt in arr])
	cy = np.mean([pt.y() for pt in arr])
	return Point(cx, cy)