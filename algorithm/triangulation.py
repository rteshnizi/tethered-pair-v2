"""
[cpp source](https://doc.cgal.org/latest/Triangulation_2/Triangulation_2_2polygon_triangulation_8cpp-example.html)

[py source](https://github.com/CGAL/cgal-swig-bindings/blob/master/examples/python/polygonal_triangulation.py)
"""

import utils.cgal.geometry as Geom
import utils.vertexUtils as VertexUtils
from model.modelService import Model
from model.triangulationEdge import TriangulationEdge
from utils.cgal.types import CgalTriangulation, ConvexHull, IntRef, Polygon, TriangulationFaceHandle, TriangulationFaceRef, convertToPoint

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
	def __init__(self, cable: list, dest2, dest1, debug=False):
		"""
		Params
		===

		boundingBox: List of 4 `Vertex`

		debug: `True` will add the edges to canvas
		"""
		self.cable = cable
		self.src1 = cable[0]
		self.src2 = cable[-1]
		self.dest1 = dest1
		self.dest2 = dest2
		# A dictionary of facesHandles (triangles) -> FaceInfo
		self.faceInfoMap = {}
		# Will be populated when finding convex hull
		self.fullyEnclosedPolygons = []
		self.partiallyEnclosedObstacles = []
		self.debug = debug
		# Maps point location to it's handle
		# This is used in finding a handle for a vertex
		self._ptHandles = {}
		# A dictionary of {Point,Point} -> TriangulationEdge
		self._canvasEdges = {}
		# The Polygon that define the boundary given by the cable before performing convex hull
		self.originalPolygon: Polygon = None
		# List of points that define the boundary of triangulation
		self.boundaryPts = []
		self._getOriginalBoundary()
		# self._dealWithPartialObstacles()
		self._getConvexHull()
		# self._debugConvexHull()

		self.cgalTri = CgalTriangulation()
		self._triangulate()
		self.triangleCount = 0
		self._countTriangles()
		if debug:
			self.drawEdges()

	def _getOriginalBoundary(self) -> None:
		extendedCable = [self.dest1] + self.cable + [self.dest2]
		self.boundaryPts = [Geom.convertToPoint(vert) for vert in extendedCable]
		self.originalPolygon = Polygon()
		for pt in self.boundaryPts:
			self.originalPolygon.push_back(pt)

	def _dealWithPartialObstacles(self) -> None:
		"""
		EXPERIMENTAL CODE: NOT IN USE
		==
		"""
		(self.fullyEnclosedPolygons, self.partiallyEnclosedObstacles) = Geom.getAllIntersectingObstacles(self.boundaryPts)
		self.fullyEnclosedPolygons = [obs.polygon for obs in self.fullyEnclosedPolygons]
		for obs in self.partiallyEnclosedObstacles:
			pts = Geom.polygonAndObstacleIntersection(self.boundaryPts, obs)
			poly = Polygon()
			for pt in pts:
				poly.push_back(pt)
			self.fullyEnclosedPolygons.append(poly)

		# re = Geom.polygonAndObstacleIntersection(self.boundaryPts, self.partiallyEnclosedObstacles[0])
		# for i in range(0, len(re) - 1):
		# 	pt1 = re[i]
		# 	pt2 = re[i + 1]
		# 	e = TriangulationEdge(model.canvas, "TE-%d" % i, [pt1, pt2], True)
		# 	e.createShape()
		# pt1 = re[0]
		# pt2 = re[-1]
		# e = TriangulationEdge(model.canvas, "TE-%d" % i, [pt1, pt2], True)
		# e.createShape()

	def _getConvexHull(self) -> None:
		"""
		Remarks
		===
		Find the convex hull of the points, then extrudes the points on the convex hull by an epsilon vector from its
		centroid.

		This is done to guarantee that the boundary of the triangulation would not intersect the constraints.

		:return: Convex Hull
		"""
		hull = []
		if not self.originalPolygon.is_simple():
			ConvexHull(self.boundaryPts, hull)
			self.boundaryPts = hull
		(self.fullyEnclosedPolygons, partials) = Geom.getAllIntersectingObstacles(self.boundaryPts)
		# Continue this until we converge
		# We converge because obstacles whose edges are on the boundary of the convex hull, technically, count as partial still
		while self.partiallyEnclosedObstacles != partials:
			for obs in partials:
				self.boundaryPts.extend(obs.polygon.vertices())
			hull = []
			ConvexHull(self.boundaryPts, hull)
			# centroid = Geom.centroid(hull)
			# extruded = []
			# for pt in hull:
			# 	vec = Geom.getEpsilonVector(centroid, pt)
			# 	extruded.append(pt + vec)
			self.boundaryPts = hull
			self.partiallyEnclosedObstacles = partials
			# (self.fullyEnclosedPolygons, self.partiallyEnclosedObstacles) = Geom.getAllIntersectingObstacles(extruded)
			(self.fullyEnclosedPolygons, partials) = Geom.getAllIntersectingObstacles(self.boundaryPts)
		# After we converge, partials are actually fully enclosed
		self.fullyEnclosedPolygons.extend(self.partiallyEnclosedObstacles)
		self.fullyEnclosedPolygons = [obs.polygon for obs in self.fullyEnclosedPolygons]

	def _debugConvexHull(self):
		for i in range(0, len(self.boundaryPts) - 1):
			pt1 = self.boundaryPts[i]
			pt2 = self.boundaryPts[i + 1]
			e = TriangulationEdge(model.canvas, "TE-%d" % i, [pt1, pt2], True)
			e.createShape()
		pt1 = self.boundaryPts[0]
		pt2 = self.boundaryPts[-1]
		e = TriangulationEdge(model.canvas, "TE-%d" % i, [pt1, pt2], True)
		e.createShape()

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
		# We need to do this because for the triangulation we extrude the boundary
		# because of that the IDs might be off by an epsilon
		# FIXME: Might be unnecessary now that we have polygon intersection
		# vrt = Geom.getClosestVertex(pt)
		# key = VertexUtils.ptToStringId(vrt) if vrt else VertexUtils.ptToStringId(pt)
		key = VertexUtils.ptToStringId(pt)
		self._ptHandles[key] = handle

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

	def _addCanvasEdge(self, segment, canvasEdge):
		pts = frozenset([VertexUtils.ptToStringId(segment.source()), VertexUtils.ptToStringId(segment.target())])
		self._canvasEdges[pts] = canvasEdge

	def _insertCableConstraints(self) -> None:
		for i in range(len(self.cable) - 1):
			h1 = self.getVertexHandle(self.cable[i])
			h2 = self.getVertexHandle(self.cable[i + 1])
			self.cgalTri.insert_constraint(h1, h2)
		h1 = self.getVertexHandle(self.src1)
		h2 = self.getVertexHandle(self.dest1)
		self.cgalTri.insert_constraint(h1, h2)
		h1 = self.getVertexHandle(self.src2)
		h2 = self.getVertexHandle(self.dest2)
		self.cgalTri.insert_constraint(h1, h2)

	def _triangulate(self):
		"""
		Construct Triangles
		"""
		# Insert exterior
		self._insertPointsIntoTriangulation(self.boundaryPts)
		# Insert interior (obstacles)
		for poly in self.fullyEnclosedPolygons:
			self._insertPointsIntoTriangulation(list(poly.vertices()))
		self._insertCableConstraints()
		self._markInteriorTriangles()

	def _countTriangles(self):
		"""
		Updates self.triangleCount
		"""
		self.triangleCount = 0
		for _f in self.cgalTri.finite_faces():
			self.triangleCount += 1

	def _isFaceSurroundedByCable(self, face: TriangulationFaceHandle):
		for i in range(3):
			pt = face.vertex(i).point()
			isOnCable = False
			for v in [self.dest1] + self.cable +[self.dest2]:
				if convertToPoint(v) == pt:
					isOnCable = True
					break
			if not isOnCable:
				return False
		return True

	def _filterNonDomainTriangle(self, face: TriangulationFaceHandle):
		if self.faceInfoMap[face].inDomain():
			return True
		if self._isFaceSurroundedByCable(face):
			return True
		return False

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
		# See _insertHandleIntoDict()
		# vrt = Geom.getClosestVertex(vertex)
		# key = VertexUtils.ptToStringId(vertex) if vrt else VertexUtils.ptToStringId(vertex)
		key = VertexUtils.ptToStringId(vertex)
		return self._ptHandles.get(key)

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
		edge = self.getCgalEdge(vertexSet)
		if not edge:
			raise RuntimeError("No edge found for the vertex set")
		(faceHandle, vertexInd) = edge
		faces = [faceHandle, faceHandle.neighbor(vertexInd)]
		faces = list(filter(self._filterNonDomainTriangle, faces))
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
			ptVert = model.getVertexByLocation(pt.x(), pt.y())
			edges.append(frozenset([vert, ptVert if ptVert else pt]))
			# edges.append(frozenset([vert, model.getVertexByLocation(pt.x(), pt.y())]))
		return frozenset(edges)

	def isPointInsideOriginalPolygon(self, vert):
		"""
		Check whether the given Vertex/Point falls inside the polygon originally given to triangulation as the boundary
		(i.e., before getting the convex hull)
		"""
		return Geom.isInsidePoly(self.originalPolygon, vert)

	def drawEdges(self, drawDomainOnly=False):
		i = 0
		# draw constraints
		for edge in self.cgalTri.finite_edges():
			i += 1
			if (not drawDomainOnly) and self.cgalTri.is_constrained(edge):
				segment = self.cgalTri.segment(edge)
				canvasE = TriangulationEdge(model.canvas, "TE-%d" % i, segment, True)
				canvasE.highlightEdge()
				self._addCanvasEdge(segment, canvasE)
		#  draw triangulation edges on top of constraints
		for edge in self.cgalTri.finite_edges():
			i += 1
			if not self.cgalTri.is_constrained(edge) and self.faceInfoMap[edge[0]].inDomain():
				segment = self.cgalTri.segment(edge)
				canvasE = TriangulationEdge(model.canvas, "TE-%d" % i, segment)
				canvasE.createShape()
				self._addCanvasEdge(segment, canvasE)

	def getCanvasEdge(self, vertexSet):
		pts = frozenset([VertexUtils.ptToStringId(convertToPoint(vert)) for vert in vertexSet])
		return self._canvasEdges[pts]

	def eraseDrawnEdges(self):
		for edge in self._canvasEdges:
			self._canvasEdges[edge].removeShape()
		self._canvasEdges = {}

	def areTrianglesNeighbor(self, faceHandle1: TriangulationFaceHandle, faceHandle2: TriangulationFaceHandle):
		return faceHandle1.has_neighbor(faceHandle2)

	def triangleHasVertex(self, faceHandle: TriangulationFaceHandle, vertex):
		vertHandle = self.getVertexHandle(vertex)
		if not vertHandle: return False
		return faceHandle.has_vertex(vertHandle)

	def getCommonEdge(self, faceHandle1: TriangulationFaceHandle, faceHandle2: TriangulationFaceHandle):
		indices = {0, 1, 2}
		for i in indices:
			neighbor = faceHandle1.neighbor(i)
			if neighbor == faceHandle2:
				ptInds = indices - {i}
				verts = [faceHandle1.vertex(j).point() for j in ptInds]
				verts = [model.getVertexByLocation(x=pt.x(), y=pt.y()) for pt in verts]
				return frozenset(verts)
		return frozenset()
