# from sympy.geometry import Point, Polygon, Ray, Segment, convex_hull
from utils.cgal.types import Point, Polygon#, Ray, Segment, convex_hull
from math import sin, sqrt

from model.model_service import Model

"""
Geometry Helper functions
"""
model = Model()
EPSILON_MULTIPLIER = 0.000001 # 1e-6

def vertexDistance(v1, v2):
	vec = v1.loc - v2.loc
	return sqrt(vec.squared_length())

def getEpsilonVector(v1, v2):
	"""
	Returns a Vect_2 which represents an epsilon vector
	"""
	v = v1.loc - v2.loc
	return v * EPSILON_MULTIPLIER

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
