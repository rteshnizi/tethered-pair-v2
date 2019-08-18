import utils.symPy.geometry as geometry
from sympy.geometry import Polygon, Segment
from model.modelService import Model
from utils.priorityQ import PriorityQ
from model.triangulationEdge import TriangulationEdge

model = Model()

def triangulate(boundingBox):
	"""
	Returns a list of triangulation edges
	Params
	===

	boundingBox: List of 4 Vertex
	"""
	edges = findInnerEdges(boundingBox)
	pts = getAllPoints(boundingBox, edges)
	(hullVerts, hull) = geometry.getConvexHullFromPoint(pts)
	for e in hull.sides:
		edges.append(e)
	createEdgeList([v.loc for v in hullVerts])
	# pQ = getPriorityQ(pts)
	# getMonotoneSubpolygons(edges)
	return None
	# return

def findInnerEdges(boundingBox):
	"""
	Returns [sympy.geometry.Segment]
	"""
	edges = []
	poly = Polygon(*[v.loc for v in boundingBox])
	inside = geometry.isInsidePoly(poly, [o.polygon for o in model.obstacles])

	for i in range(0, len(inside)):
		if (inside[i]):
			edges = edges + model.obstacles[i].polygon.sides
	return edges

def getAllPoints(boundingBox, edges):
	pts = list(sum([edge.points for edge in edges], ()))
	for v in boundingBox:
		pts.append(v.loc)
	return pts

def getPriorityQ(pts):
	pQ = PriorityQ(key = pointComparator)
	for pt in pts:
		pQ.enqueue(pt)
	return pQ

def getMonotoneSubpolygons(verts):
	_edges = createEdgeList(verts)
	q = PriorityQ(initial = verts, key = pointComparator)
	for i in range(0, len(verts)):
		q.enqueue(verts[i])
	while (not q.isEmpty()):
		handleVert(q.dequeue())
	return 0

def handleVert(vert):
	pass

def createEdgeList(verts):
	edges = []
	n = len(verts)
	for i in range(0, n):
		e = None
		if (i == n - 1):
			e = TriangulationEdge(model.canvas, "TE%d" % i, [verts[-1], verts[0]])
		else:
			e = TriangulationEdge(model.canvas, "TE%d" % i, [verts[i], verts[i + 1]])
		e.createShape()
		edges.append(e)
	return edges

def pointComparator(pt):
	return -(1000000 * pt.y) + pt.x
