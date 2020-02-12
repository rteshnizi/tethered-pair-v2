from typing import List
import numpy as np
from utils.cgal.types import Line, Point, PointOrSegmentNone, Polygon, Ray, Segment, Vector, crossProduct, intersection
import utils.shapely.geometry as SHGeom
from utils.vertexUtils import convertToPoint, removeRepeatedVertsOrdered, SMALL_DISTANCE
from math import sqrt, fabs, nan

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

def getUnitVectorFromVect(vect) -> Vector:
	"""
	Returns a Vector which represents an epsilon vector
	"""
	l = sqrt(vect.squared_length())
	vect = (vect / l)
	return vect

def getUnitVector(frm, to) -> Vector:
	"""
	Returns a Vector which represents an epsilon vector
	"""
	toPt = convertToPoint(to)
	frmPt = convertToPoint(frm)
	return getUnitVectorFromVect(toPt - frmPt)

def getEpsilonVectorFromVect(vect) -> Vector:
	"""
	Returns a Vector which represents an epsilon vector
	"""
	vect = getUnitVectorFromVect(vect)
	return vect * EPSILON_MULTIPLIER

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
	poly = Polygon([convertToPoint(v) for v in vertices])
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

def circleAndLineSegmentIntersection(pt1, pt2, center, radius):
	return SHGeom.circleAndLineSegmentIntersection(pt1, pt2, center, radius)

def pointAndLineDistance(pt, lPt1, lPt2):
	"""https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points"""
	pt = convertToPoint(pt)
	(x0, y0) = (pt.x(), pt.y())
	lPt1 = convertToPoint(lPt1)
	(x1, y1) = (lPt1.x(), lPt1.y())
	lPt2 = convertToPoint(lPt2)
	(x2, y2) = (lPt2.x(), lPt2.y())
	d = fabs(((y2 - y1) * x0) - ((x2 - x1) * y0) + x2 * y1 - y2 * x1) / vertexDistance(lPt1, lPt2)
	return d

def reversePythagorean(hypotenuse, a):
	"""given the length of hypotenuse and one of the right angle sides, find the other"""
	return sqrt(hypotenuse * hypotenuse - a * a)

def getLineSegAndRayIntersection(ls1, ls2, rayFrom, rayTo):
	lsPt1 = convertToPoint(ls1)
	lsPt2 = convertToPoint(ls2)
	ryPt1 = convertToPoint(rayFrom)
	ryPt2 = convertToPoint(rayTo)
	l = Segment(lsPt1, lsPt2)
	r = Ray(ryPt1, ryPt2)
	pt = intersection(l, r)
	pass

def getPointOnLineSegmentFraction(ls1, ls2, pt):
	"""
	Given a line segment (that has direction) from ls1 to ls2, what fraction of the line does pt fall on
	"""
	ls1 = convertToPoint(ls1)
	ls2 = convertToPoint(ls2)
	segment = Segment(ls1, ls2)
	if not segment.has_on(pt): return nan
	v1 = segment.to_vector()
	pt = convertToPoint(pt)
	v2 = pt - ls1
	areInSameDirection = True if (v2 * v1) >= 0 else False
	d1 = sqrt(v1.squared_length())
	d2 = sqrt(v2.squared_length())
	return d1 / d2 if areInSameDirection else -1 * (d1 / d2)

def getPointOnLineSegment(v1, v2, frac) -> Point:
	"""
	given frac in [0,1] find the point that falls an frac of the distance from v1 to v2
	"""
	v1 = convertToPoint(v1)
	v2 = convertToPoint(v2)
	vect = v1 - v2
	return v1 + (vect * frac)

def reza(src, dst, pt, d):
	src = convertToPoint(src)
	dst = convertToPoint(dst)
	s1 = Segment(src, dst)
	l1 = s1.supporting_line()
	pt = convertToPoint(pt)
	l2  = l1.perpendicular(pt)
	inter = intersection(l1, l2)
	v1 = getUnitVector(src, dst)
	end = inter + v1 * d
	return getPointOnLineSegmentFraction(src, dst, end)
