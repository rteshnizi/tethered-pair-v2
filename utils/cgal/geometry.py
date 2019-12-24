from typing import List
import numpy as np
from utils.cgal.types import Line, Point, PointOrSegmentNone, Polygon, Segment, Vector, crossProduct, intersection
import utils.shapely.geometry as SHGeom
from utils.vertexUtils import convertToPoint, removeRepeatedVertsOrdered, SMALL_DISTANCE
from math import sqrt

from model.modelService import Model

"""
Geometry Helper functions
"""
model = Model()
EPSILON_MULTIPLIER = SMALL_DISTANCE / 2 # in pixels

def vertexDistance(v1, v2):
	pt1 = convertToPoint(v1)
	pt2 = convertToPoint(v2)
	vec = pt1 - pt2
	return sqrt(vec.squared_length())

def getEpsilonVectorFromVect(vect) -> Vector:
	"""
	Returns a Vector which represents an epsilon vector
	"""
	l = sqrt(vect.squared_length())
	vect = (vect / l) * EPSILON_MULTIPLIER
	return vect

def getEpsilonVector(frm, to) -> Vector:
	"""
	Returns a Vector which represents an epsilon vector
	"""
	toPt = convertToPoint(to)
	frmPt = convertToPoint(frm)
	return getEpsilonVectorFromVect(toPt - frmPt)

def isInsidePoly(poly, pt) -> bool:
	"""
	Check if point `pt` is inside Polygon `poly`
	"""
	return poly.has_on_bounded_side(convertToPoint(pt))

def isOnPoly(poly: Polygon, pt) -> bool:
	"""
	Check if point `pt` is inside Polygon `poly`
	"""
	return poly.has_on_boundary(convertToPoint(pt))

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
		poly.push_back(convertToPoint(vert))
	for obs in model.obstacles:
		isIn = False
		isOut = False
		for pt in obs.vertices:
			# if isInsidePoly(poly, pt) or isOnPoly(poly, pt):
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

# FIXME: This method is buggy. I have seen a case where line.has_on(pt2) == False
# def isColinear(ref1, ref2, target) -> bool:
# 	"""
# 	Given the two reference points, determine if target is colinear with line segment formed by ref1->ref2
# 	"""
# 	pt1 = convertToPoint(ref1)
# 	pt2 = convertToPoint(ref2)
# 	ptTarget = convertToPoint(target)

# 	line = Line(pt1, pt2)
# 	return line.has_on(ptTarget)

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

def isToTheLeft(ref1, ref2, target) -> bool:
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
	return cVec3D.z() < 0

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

def intersectPolygonAndSegment(poly: Polygon, segment: Segment) -> List[PointOrSegmentNone]:
	if not isinstance(poly, Polygon):
		raise TypeError("poly should be a Polygon")
	if not isinstance(segment, Segment):
		raise TypeError("line should be a Segment")
	intersections = []
	for edge in poly.edges():
		res = intersection(segment, edge)
		if res:
			intersections.append(res)
	return intersections

def intersectSegmentAndSegment(src1, dest1, src2, dest2) -> List[PointOrSegmentNone]:
	pts = [convertToPoint(pt) for pt in [src1, dest1, src2, dest2]]
	seg1 = Segment(pts[0], pts[1])
	seg2 = Segment(pts[2], pts[3])
	return intersection(seg1, seg2)

def extrudeVertsWithEpsilonVect(verts) -> List[Point]:
	centroidPt = centroid(verts)
	extruded = []
	for v in verts:
		pt = convertToPoint(v)
		vec = getEpsilonVector(centroidPt, pt)
		extruded.append(pt + vec)
	return extruded

def polygonAndObstacleIntersection(polyVerts, obstacle) -> List[Point]:
	result = SHGeom.polygonIntersection(polyVerts, obstacle.polygon.vertices())
	result = removeRepeatedVertsOrdered(result)
	return result

def addVectorToPoint(pt, dx, dy):
	vect = Vector(dx, dy)
	_pt = convertToPoint(pt)
	return _pt + vect

def isVisible(v1, v2):
	pt1 = convertToPoint(v1)
	pt2 = convertToPoint(v2)
	l = Segment(pt1, pt2)
	for o in model.obstacles:
		intersections = o.intersection(l)
		# if vertices are visible, the intersection is either empty or it is a line segment
		# whose at least one of the end points is one of the two vertices
		if (len(intersections) == 0):
			continue
		# If obstacles are concave, we might have more than 2 intersections
		for intersection in intersections:
			if isinstance(intersection, Point):
				if not (intersection == pt1 or intersection == pt2):
					return False
			else: # intersection is a Segment
				# Segments show that an edge is tangent to the visibility ray
				# They don't block visibility
				pass
	return True
