from utils.cgal.types import Line, Point, Polygon, Segment, Vector, convertToPoint, crossProduct
from math import sin, sqrt

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

def getEpsilonVector(v1, v2) -> Vector:
	"""
	Returns a Vector which represents an epsilon vector
	"""
	pt1 = convertToPoint(v1)
	pt2 = convertToPoint(v2)
	vec = pt1 - pt2
	return vec * EPSILON_MULTIPLIER

def getInnerVertices(v1, v2, v3):
	poly = Polygon(v1.loc, v2.loc, v3.loc)
	inner = []
	if (isinstance(poly, Segment)):
		return inner
	for v in model.vertices:
		if (poly.encloses_point(v.loc)):
			inner.append(v)
	return inner

def getConvexHullFromVertex(vertList):
	return getConvexHullFromPoint([v.loc for v in vertList])

def getConvexHullFromPoint(ptList):
	if (len(ptList) < 4):
		return (ptList, Polygon(*ptList))
	hull = convex_hull(*[(v.x, v.y) for v in ptList])
	hullVerts = hull.vertices
	return ([model.getVertexByLocation(v.x, v.y) for v in hullVerts], hull)

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
	"""
	result = []
	poly = Polygon()
	for vert in vertices:
		poly.push_back(vert.loc)
	for obs in model.obstacles:
		for pt in obs.vertices:
			if (isInsidePoly(poly, pt)):
				result.append(obs)
				break
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
