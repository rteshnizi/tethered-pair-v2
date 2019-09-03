from typing import List
import numpy as np
from utils.cgal.types import Line, Point, PointOrSegmentNone, Polygon, Segment, Vector, convertToPoint, crossProduct, intersection
import utils.shapely.geometry as SHGeom
import utils.vertexUtils as VertexUtils
from math import sqrt

from model.modelService import Model

"""
Geometry Helper functions
"""
model = Model()
SMALL_DISTANCE = 0.001 # 1e-3
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

def intersectPolygonAndSegment(poly, segment) -> List[PointOrSegmentNone]:
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

def getClosestVertex(pt):
	for v in model.robots:
		if vertexDistance(pt, v) < SMALL_DISTANCE:
			return v
		if vertexDistance(pt, v.destination) < SMALL_DISTANCE:
			return v.destination

	for v in model.vertices:
		if vertexDistance(pt, v) < SMALL_DISTANCE:
			return v

def polygonAndObstacleIntersection(polyVerts, obstacle) -> List[Point]:
	result = SHGeom.polygonIntersection(polyVerts, obstacle.polygon.vertices())
	result = VertexUtils.removeRepeatedVertsOrdered(result)
	return result

def addVectorToPoint(pt, dx, dy):
	vect = Vector(dx, dy)
	_pt = convertToPoint(pt)
	return _pt + vect
