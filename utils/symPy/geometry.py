from sympy.geometry import Point, Polygon, Ray, Segment, convex_hull
from math import sin

from model.modelService import Model

"""
Geometry Helper functions
"""
model = Model()
EPSILON_MULTIPLIER = 0.000001 # 1e-6

def vertexDistance(v1, v2):
	return v1.loc.distance(v2.loc)

def createSegmentFromVertices(v1, v2):
	return Segment(v1.loc, v2.loc)

def createPolygonFromVertices(verts):
	return Polygon([v.loc for v in verts])

def getEpsilonVector(v1, v2):
	"""
	Returns a Point which represents an epsilon vector
	"""
	v = v1.loc - v2.loc
	return v * EPSILON_MULTIPLIER

def cross(vec1, vec2):
	"""
	vec1: sympy.geometry.points.Point

	vec2: sympy.geometry.points.Point
	"""
	origin = Point(0, 0)
	l1 = vec1.distance(origin)
	l2 = vec2.distance(origin)
	r1 = Ray(origin, vec1)
	r2 = Ray(origin, vec2)
	angle = r1.angle_between(r2)
	return l1 * l2 * sin(angle)

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

def isInsidePoly(poly1, polyList):
	"""
	Given a polygon, decide whether the others are partially or fully intersect

	Params
	===
	poly1: the source polygon sympy.geometry.polygon

	polyList: list of polygons to check if they are inside poly1 [sympy.geometry.Polygon]
	"""
	n = len(polyList)
	result = [False] * n
	for i in range(0, n):
		poly2 = polyList[i]
		for pt in poly2.vertices:
			if (poly1.encloses_point(pt)):
				result[i] = True
				break
	return result
