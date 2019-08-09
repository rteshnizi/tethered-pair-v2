"""
[cpp source](https://doc.cgal.org/latest/Triangulation_2/Triangulation_2_2polygon_triangulation_8cpp-example.html)

[py source](https://github.com/CGAL/cgal-swig-bindings/blob/master/examples/python/polygonal_triangulation.py)
"""

import utils.cgal.geometry as Geom
from model.model_service import Model
from model.triangulationEdge import TriangulationEdge
from utils.cgal.types import CgalTriangulation, ConvexHull, IntRef, TriangulationFaceRef
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

		# A dictionary of facesHandles (triangles) -> FaceInfo
		self.faceInfoMap = {}
		self.obstacles = []
		self.debug = debug
		# Maps point location to it's handle
		# This is used in finding a handle for a vertex
		self._ptHandles = {}
		# A dictionary of {Point,Point} -> TriangulationEdge
		self._canvasEdges = {}

		# Fix cases where bounding box has repeated vertices
		self.boundingBox = self._removeRepeatedVerts(boundingBox)
		self.boundaryPts = [vert.loc for vert in boundingBox]
		innerPts = self._findInnerPoints()
		self.boundaryPts.extend(innerPts)
		self.boundaryPts = self._getConvexHull()
		self.cgalTri = CgalTriangulation()
		self.triangulate()
		if debug:
			self.drawEdges()

	def _ptToStringId(self, pt):
		"""
		Use this method internally to obtain a unique Id for each point in this triangulation
		"""
		return '%d,%d' % (pt.x(), pt.y())

	def _removeRepeatedVerts(self, verts):
		vertDict = {}
		for vert in verts:
			vertDict[vert.name] = vert
		return list(vertDict.values())

	def _getConvexHull(self):
		hull = []
		ConvexHull(self.boundaryPts, hull)
		return hull

	def _findInnerPoints(self):
		pts = []
		obstacles = Geom.getAllIntersectingObstacles(self.boundingBox)
		for obs in obstacles:
			pts.extend(obs.polygon.vertices())
		return pts

	def _insertPointsIntoTriangulation(self, pts):
		"""
		Adds points to this triangulation while maintaining the handles in the `_ptHandles` dictionary

		Remarks
		===
		This method should be called per entity.
		That is, all of the points that belong to one hole (obstacle) should be added at once and separately.
		"""
		if not pts:
			return

		handles = []
		for pt in pts:
			handle = self.cgalTri.insert(pt)
			self._insertHandleIntoDict(pt, handle)
			handles.append(handle)
		for i in range(len(pts) - 1):
			self.cgalTri.insert_constraint(handles[i], handles[i + 1])
		self.cgalTri.insert_constraint(handles[-1], handles[0])

	def _insertHandleIntoDict(self, pt, handle):
		self._ptHandles[self._ptToStringId(pt)] = handle

	def _markInteriorTriangles(self):
		"""
		Populates `self.faceInfoMap`

		Remarks
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
		self._markInteriorTrianglesBFS(self.cgalTri.infinite_face(), 0, borders)
		while borders != []:
			edge = borders[0]		# border.front
			borders = borders[1:]	# border.pop_front
			neighboringFace = edge[0].neighbor(edge[1]) # Edge is a tuple (face, vertexIndex) (see https://doc.cgal.org/latest/Triangulation_2/index.html#title3)
			if self.faceInfoMap[neighboringFace].isMarked():
				continue
			lvl = self.faceInfoMap[edge[0]].nestingLevel + 1
			self._markInteriorTrianglesBFS(neighboringFace, lvl, borders)

	def _markInteriorTrianglesBFS(self, startFace, nestingLvl, borderEdges):
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

	def _convertToPoint(self, vert):
		"""
		Utility function that takes a Vertex or Point and returns a Point
		"""
		return vert.loc if vert.loc else vert

	def _addCanvasEdge(self, segment, canvasEdge):
		pts = frozenset([self._ptToStringId(segment.source()), self._ptToStringId(segment.target())])
		self._canvasEdges[pts] = canvasEdge

	def triangulate(self):
		"""
		Construct Triangles
		"""
		# Insert exterior
		self._insertPointsIntoTriangulation(self.boundaryPts)
		# Insert interior (obstacles)
		self.obstacles = Geom.getAllIntersectingObstacles(self.boundingBox)
		for obs in self.obstacles:
			self._insertPointsIntoTriangulation([vert.loc for vert in obs.vertices])
		self._markInteriorTriangles()

	def getCgalEdge(self, vertexSet):
		"""
		Finds the edge connecting the two points in vertexSet, or `None` if ti doesn't exist.


		Params
		===
		vertexSet: A set of two vertices

		Remarks
		===
		An Edge in CGAL TRiangulation is a tuple (faceHandle, vertexIndex)

		[read more](https://doc.cgal.org/latest/Triangulation_2/index.html#title3)
		"""
		# The input can be a vertex or a cgal Point
		if (len(vertexSet) != 2):
			raise RuntimeError("vertexSet must have two members")
		pts = [self.getVertexHandle(v) for v in vertexSet]
		if (not pts[0] or not pts[1]):
			return None
		faceHandleRef = TriangulationFaceRef()
		vertexIndRef = IntRef()
		if (not self.cgalTri.is_edge(pts[0], pts[1], faceHandleRef, vertexIndRef)):
			return None
		faceHandle = faceHandleRef.object()
		vertexInd = vertexIndRef.object()
		return (faceHandle, vertexInd)

	def getVertexHandle(self, vertex):
		"""
		Returns
		===
		The handle to the point representing this vertex in the triangulation

		Params
		===
		vertex: model.vertex.Vertex or utils.cgal.types.Point
		"""
		pt = self._convertToPoint(vertex)
		return self._ptHandles.get(self._ptToStringId(pt))

	def getIncidentTriangles(self, vertexSet):
		"""
		Finds the edge connecting the two points in vertexSet, if it exists, and returns a set of the two face [handles] incident to the edge

		Params
		===
		vertexSet: A set of two vertices

		Remarks
		===
		For more details see
		[this](https://github.com/CGAL/cgal-swig-bindings/blob/7850024f5051eeec492aa3042d0b267c875cd5c5/examples/python/test_t2.py#L49)
		and
		[this](http://cgal-discuss.949826.n4.nabble.com/How-to-get-two-faces-incident-to-a-edge-in-Delaunay-Triangulation-td4655759.html)
		"""
		(faceHandle, vertexInd) = self.getCgalEdge(vertexSet)
		faces = [faceHandle, faceHandle.neighbor(vertexInd)]
		faces = list(filter(lambda f: self.faceInfoMap[f].inDomain(), faces))
		return frozenset(faces)

	def getIncidentEdges(self, vert, faceHandle):
		"""
		Given a vertex and face handle, find the two edges incident to it

		Returns
		===
		A set of two sets, each containing a pair of vertices to represent an edge
		"""
		vertHandle = self.getVertexHandle(vert)
		ind = faceHandle.index(vertHandle)
		indices = {0, 1, 2} - {ind}
		edges = []
		for i in indices:
			pt = faceHandle.vertex(i).point()
			edges.append(frozenset([vert, model.getVertexByLocation(pt.x(), pt.y())]))
		return frozenset(edges)

	def drawEdges(self, drawDomainOnly=False):
		i = 0
		for edge in self.cgalTri.finite_edges():
			i += 1
			if (not drawDomainOnly) and self.cgalTri.is_constrained(edge):
				segment = self.cgalTri.segment(edge)
				canvasE = TriangulationEdge(model.canvas, "TE-%d" % i, segment, True)
				canvasE.createShape()
				self._addCanvasEdge(segment, canvasE)
			elif self.faceInfoMap[edge[0]].inDomain():
				segment = self.cgalTri.segment(edge)
				canvasE = TriangulationEdge(model.canvas, "TE-%d" % i, segment)
				canvasE.createShape()
				self._addCanvasEdge(segment, canvasE)

	def getCanvasEdge(self, vertexSet):
		pts = frozenset([self._ptToStringId(self._convertToPoint(vert)) for vert in vertexSet])
		return self._canvasEdges[pts]

	def eraseDrawnEdges(self):
		for edge in self._canvasEdges:
			self._canvasEdges[edge].removeShape()
		self._canvasEdges = {}
