import utils.cgal.geometry as Geom
from model.entity import Entity
from model.modelService import Model
from model.vertex import Vertex
from utils.cgal.drawing import CreatePolygon
from utils.cgal.types import Polygon
from utils.vertexUtils import ptToStringId, convertToPoint

OBSTACLE_COLOR = "Grey"
mode = Model()

class Obstacle(Entity):
	def __init__(self, name, pts):
		"""
		canvas: tk.Canvas

		color: color string

		name: str

		pts: [utils.cgal.types.Point]
		"""
		super().__init__(color=OBSTACLE_COLOR, name=name)
		self.vertices = []
		self._vertexByLocation = {}
		self._pts = pts
		self.polygon = Polygon(self._pts)
		self.createVertices(pts)

	def createVertices(self, pts):
		for i in range(0, len(pts)):
			v = Vertex(name="%s-%d" % (self.name, i), loc=pts[i], ownerObs=self)
			self.vertices.append(v)
			self._vertexByLocation[ptToStringId(v)] = v

	def createShape(self, canvas):
		if self.canvasId: return
		self.canvas = canvas
		self.canvasId = CreatePolygon(canvas=self.canvas.tkCanvas, pointsList=self._pts, outline="", fill=self.color, width=1, tag=self.name)

	def enclosesPoint(self, pt):
		return Geom.isInsidePoly(self.polygon, convertToPoint(pt))

	def getVertex(self, pt) -> Vertex:
		return self._vertexByLocation.get(ptToStringId(pt), None)

	def areAdjacent(self, pt1, pt2) -> bool:
		v1 = self.getVertex(pt1)
		if not v1: return False
		v2 = self.getVertex(pt2)
		if not v2: return False
		return v2 in v1.adjacentOnObstacle

	def intersection(self, line):
		"""
		Intersect this obstacle with the line segment formed by the two given points
		"""
		return Geom.intersectPolygonAndSegment(self.polygon, line)
