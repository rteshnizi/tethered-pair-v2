import utils.cgal.geometry as Geom
from model.entity import Entity
from model.modelService import Model
from model.vertex import Vertex
from utils.cgal.drawing import CreatePolygon
from utils.cgal.types import Polygon

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
		self._pts = pts
		self.polygon = Polygon()
		for pt in self._pts:
			self.polygon.push_back(pt)
		self.createVertices(pts)

	def createVertices(self, pts):
		for i in range(0, len(pts)):
			v = Vertex(name="%s-%d" % (self.name, i), loc=pts[i], ownerObs=self)
			self.vertices.append(v)

	def createShape(self, canvas):
		if self.canvasId: return
		self.canvas = canvas
		self.canvasId = CreatePolygon(canvas=self.canvas.tkCanvas, pointsList=self._pts, outline="", fill=self.color, width=1, tag=self.name)

	def enclosesVertex(self, vrt):
		return self.enclosesPoint(vrt.loc)

	def enclosesPoint(self, pt):
		return Geom.isInsidePoly(self.polygon, pt)

	def intersection(self, line):
		"""
		Intersect this obstacle with the line segment formed by the two given points
		"""
		return Geom.intersectPolygonAndSegment(self.polygon, line)
