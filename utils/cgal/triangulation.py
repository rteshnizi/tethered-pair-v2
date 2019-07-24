"""
[cpp source](https://doc.cgal.org/latest/Triangulation_2/Triangulation_2_2polygon_triangulation_8cpp-example.html)

[py source](https://github.com/CGAL/cgal-swig-bindings/blob/master/examples/python/polygonal_triangulation.py)
"""

import utils.cgal.geometry as Geom
from model.model_service import Model
from model.triangulationEdge import TriangulationEdge
from utils.cgal.types import Triangulation
from utils.priorityQ import PriorityQ

model = Model()

class FaceInfo(object):
	def __init__(self):
		self.nestingLevel = -1

	def isMarked(self):
		return self.nestingLevel != -1

	def inDomain(self):
		return (self.nestingLevel % 2) == 1

def triangulate(boundingBox, debug=False):
	"""
	Returns a list of triangulation edges
	Params
	===

	boundingBox: List of 4 `Vertex`
	"""
	# FIXME: Fix boundingBox according to convex hull
	if len(boundingBox) != 4:
		raise RuntimeError("boundingBox must be a list of 4 Vertex")
	tri = Triangulation()
	innerPts = findInnerPoints(boundingBox)
	# Insert exterior
	insertPointsIntoTriangulation(tri, [vert.loc for vert in boundingBox])
	# Insert interior
	insertPointsIntoTriangulation(tri, innerPts)

	faceInfo = markInteriorTriangles(tri)
	if debug:
		drawEdges(tri, faceInfo)
	return None
	# return

def findInnerPoints(boundingBox):
	pts = []
	obstacles = Geom.getAllIntersectingObstacles(boundingBox)
	for obs in obstacles:
		pts.extend(obs.polygon.vertices())
	return pts
	# return [vert.loc for vert in model.obstacles[0].vertices]

def insertPointsIntoTriangulation(triangulation, pts):
	if not pts:
		return

	handles = [triangulation.insert(pt) for pt in pts]
	for i in range(len(pts)-1):
		triangulation.insert_constraint(handles[i], handles[i + 1])
	triangulation.insert_constraint(handles[-1], handles[0])

def markInteriorTriangles(triangulation):
	"""
	Returns
	===
	A dictionary of faces (triangles) -> FaceInfo

	Details
	===
	Explore the set of facets connected with non constrained edges,
	and attribute to each such set a nesting level.

	We start from the facets incident to the infinite vertex, with a
	nesting level of 0. Then we recursively consider the non-explored
	facets incident to constrained edges bounding the former set and
	increase the nesting level by 1.

	Facets in the domain are those with an odd nesting level.
	"""
	faceInfo = {}
	for face in triangulation.all_faces():
		faceInfo[face] = FaceInfo()
	borders = []
	markInteriorTrianglesBFS(triangulation, triangulation.infinite_face(), 0, borders, faceInfo)
	while borders != []:
		edge = borders[0]		# border.front
		borders = borders[1:]	# border.pop_front
		neighboringFace = edge[0].neighbor(edge[1]) # Edge is a tuple (face, vertexIndex) (see https://doc.cgal.org/latest/Triangulation_2/index.html#title3)
		if faceInfo[neighboringFace].isMarked():
			continue
		lvl = faceInfo[edge[0]].nestingLevel + 1
		markInteriorTrianglesBFS(triangulation, neighboringFace, lvl, borders, faceInfo)
	return faceInfo

def markInteriorTrianglesBFS(triangulation, startFace, nestingLvl, borderEdges, faceInfo):
	if faceInfo[startFace].isMarked():
		return
	queue = [startFace]
	while queue != []:
		face = queue[0]		# queue.front
		queue = queue[1:]	# queue.pop_front
		if faceInfo[face].isMarked():
			continue
		faceInfo[face].nestingLevel = nestingLvl
		for i in range(3):
			edge = (face, i) # Edges are identified by a face and a vertex (see https://doc.cgal.org/latest/Triangulation_2/index.html#title3)
			neighboringFace = face.neighbor(i)
			if faceInfo[neighboringFace].isMarked():
				continue
			if triangulation.is_constrained(edge): # A non-triangulation edge is a constrained edge (see https://doc.cgal.org/latest/Triangulation_2/index.html#title23)
				borderEdges.append(edge)
			else:
				queue.append(neighboringFace)

def drawEdges(triangulation, faceInfo):
	i = 0
	for edge in triangulation.finite_edges():
		i += 1
		# if triangulation.is_constrained(edge):
		# 	continue
		# 	# plot_edge(edge, 'r-')
		# if faceInfo[edge[0]].inDomain():
		# 	segment = triangulation.segment(edge)
		# 	canvasEdge = TriangulationEdge(model.canvas, "TE-%d" % i, segment)
		# 	canvasEdge.createShape()
		# 	# plot_edge(edge, 'b-')
		segment = triangulation.segment(edge)
		canvasEdge = TriangulationEdge(model.canvas, "TE-%d" % i, segment)
		canvasEdge.createShape()
