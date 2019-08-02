"""
[cpp source](https://doc.cgal.org/latest/Triangulation_2/Triangulation_2_2polygon_triangulation_8cpp-example.html)

[py source](https://github.com/CGAL/cgal-swig-bindings/blob/master/examples/python/polygonal_triangulation.py)
"""

import utils.cgal.geometry as Geom
from model.model_service import Model
from model.triangulationEdge import TriangulationEdge
from utils.cgal.types import CgalTriangulation, ConvexHull
from utils.priorityQ import PriorityQ

model = Model()

class FaceInfo(object):
	"""
	Used in determining holes
	"""
	def __init__(self):
		self.nestingLevel = -1

	def isMarked(self):
		return self.nestingLevel != -1

	def inDomain(self):
		return (self.nestingLevel % 2) == 1

class Triangulation(object):
	def __init__(self, boundingBox, debug=False):
		"""
		Params
		===

		boundingBox: List of 4 `Vertex`

		debug: `True` will add the edges to canvas
		"""
		if len(boundingBox) != 4:
			raise RuntimeError("boundingBox must be a list of 4 Vertex")

		self.debug = debug
		# Fix cases where bounding box has repeated vertices
		self.boundingBox = self.__removeRepeatedVerts(boundingBox)
		self.boundaryPts = self.__getConvexHull([vert.loc for vert in self.boundingBox])
		# self.boundaryPts = self.__getConvexHull([vert.loc for vert in boundingBox].extend(self.__findInnerPoints()))
		self.obstacles = []
		self.cgalTri = CgalTriangulation()
		# A dictionary of faces (triangles) -> FaceInfo
		self.faceInfoMap = {}
		self.canvasEdges = []
		self.faceInfoMap = self.triangulate()
		if debug:
			self.drawEdges()

	def triangulate(self):
		"""
		Construct Triangles
		"""
		# Insert exterior
		self.__insertPointsIntoTriangulation(self.boundaryPts)
		# Insert interior (obstacles)
		self.obstacles = Geom.getAllIntersectingObstacles(self.boundingBox)
		for obs in self.obstacles:
			self.__insertPointsIntoTriangulation([vert.loc for vert in obs.vertices])
		self.__markInteriorTriangles()

	def __removeRepeatedVerts(self, verts):
		vertDict = {}
		for vert in verts:
			vertDict[vert.name] = vert
		return list(vertDict.values())

	def __getConvexHull(self, pts):
		return pts
		# FIXME: Code crashes
		# hull = []
		# ConvexHull(pts, hull)
		# return hull

	def __findInnerPoints(self):
		pts = []
		obstacles = Geom.getAllIntersectingObstacles(self.boundingBox)
		for obs in obstacles:
			pts.extend(obs.polygon.vertices())
		return pts

	def __insertPointsIntoTriangulation(self, pts):
		if not pts:
			return

		handles = [self.cgalTri.insert(pt) for pt in pts]
		for i in range(len(pts) - 1):
			self.cgalTri.insert_constraint(handles[i], handles[i + 1])
		self.cgalTri.insert_constraint(handles[-1], handles[0])

	def __markInteriorTriangles(self):
		"""
		Populates `self.faceInfoMap`

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
		for face in self.cgalTri.all_faces():
			self.faceInfoMap[face] = FaceInfo()
		borders = []
		self.__markInteriorTrianglesBFS(self.cgalTri.infinite_face(), 0, borders)
		while borders != []:
			edge = borders[0]		# border.front
			borders = borders[1:]	# border.pop_front
			neighboringFace = edge[0].neighbor(edge[1]) # Edge is a tuple (face, vertexIndex) (see https://doc.cgal.org/latest/Triangulation_2/index.html#title3)
			if self.faceInfoMap[neighboringFace].isMarked():
				continue
			lvl = self.faceInfoMap[edge[0]].nestingLevel + 1
			self.__markInteriorTrianglesBFS(neighboringFace, lvl, borders)

	def __markInteriorTrianglesBFS(self, startFace, nestingLvl, borderEdges):
		if self.faceInfoMap[startFace].isMarked():
			return
		queue = [startFace]
		while queue != []:
			face = queue[0]		# queue.front
			queue = queue[1:]	# queue.pop_front
			if self.faceInfoMap[face].isMarked():
				continue
			self.faceInfoMap[face].nestingLevel = nestingLvl
			for i in range(3):
				edge = (face, i) # Edges are identified by a face and a vertex (see https://doc.cgal.org/latest/Triangulation_2/index.html#title3)
				neighboringFace = face.neighbor(i)
				if self.faceInfoMap[neighboringFace].isMarked():
					continue
				if self.cgalTri.is_constrained(edge): # A non-triangulation edge is a constrained edge (see https://doc.cgal.org/latest/Triangulation_2/index.html#title23)
					borderEdges.append(edge)
				else:
					queue.append(neighboringFace)

	def drawEdges(self, drawDomainOnly=False):
		i = 0
		for edge in self.cgalTri.finite_edges():
			i += 1
			if (not drawDomainOnly) and self.cgalTri.is_constrained(edge):
				segment = self.cgalTri.segment(edge)
				canvasE = TriangulationEdge(model.canvas, "TE-%d" % i, segment, True)
				canvasE.createShape()
				self.canvasEdges.append(canvasE)
			elif self.faceInfoMap[edge[0]].inDomain():
				segment = triangulation.segment(edge)
				canvasE = TriangulationEdge(model.canvas, "TE-%d" % i, segment)
				canvasE.createShape()
				self.canvasEdges.append(canvasE)

	def eraseDrawnEdges(self):
		for edge in self.canvasEdges:
			edge.removeShape()
		self.canvasEdges = []
