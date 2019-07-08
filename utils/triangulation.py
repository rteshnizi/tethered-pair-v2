from sympy.geometry.polygon import Polygon

import utils.geometry as geometry
from model.model_service import Model
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
	edges = FindInnerEdges(boundingBox)
	pts = getPriorityQ(edges)
	return getMonotoneSubpolygons(edges)

def FindInnerEdges(boundingBox):
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

def getPriorityQ(edges):
	pQ = PriorityQ(key = pointComparator)
	pts = [edge.points for edge in edges]
	for pt in pts:
		pQ.enqueue(pt[0])
		pQ.enqueue(pt[1])
	return pQ

def getMonotoneSubpolygons(verts):
	edges = createEdgeList(verts)
	q = PriorityQ(initial = verts, key = pointComparator)
	for i in range(0, len(verts)):
		q.enqueue(verts[i])
	while (not q.isEmpty()):
		handleVert(q.dequeue)
	return 0

def createEdgeList(verts):
	edges = []
	n = len(verts)
	for i in range(0, n):
		if (i == n - 1):
			edges.append(TriangulationEdge(model.canvas, "TE%d" % i, [verts[-1], verts[0]]))
		else:
			edges.append(TriangulationEdge(model.canvas, "TE%d" % i, [verts[i], verts[i + 1]]))
	return edges

def pointComparator(pt):
	return -(1000000 * pt.y) + pt.x
