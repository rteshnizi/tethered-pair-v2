import utils.cgal.geometry as Geom
from model.entity import Entity
from model.modelService import Model
from model.vertex import Vertex
from utils.cgal.drawing import CreatePolygon
from utils.cgal.types import Polygon

OBSTACLE_COLOR = "Grey"
mode = Model()

class Obstacle(Entity):
	def __init__(self, canvas, name, pts):
		"""
		canvas: tk.Canvas

		color: color string

		name: str

		pts: [utils.cgal.types.Point]
		"""
		super().__init__(canvas=canvas, color=OBSTACLE_COLOR, name=name)
		self.vertices = []
		self.polygon = None
		self.createVertices(pts)
		self.createShape(pts)

	def createVertices(self, pts):
		for i in range(0, len(pts)):
			v = Vertex(canvas=self.canvas, name="%s-%d" % (self.name, i), loc=pts[i], ownerObs=self, render=True)
			self.vertices.append(v)

	def createShape(self, pts):
		if (self.canvasId): return
		self.canvasId = CreatePolygon(canvas=self.canvas, pointsList=pts, outline="", fill=self.color, width=1, tag=self.name)
		self.polygon = Polygon()
		for pt in pts:
			self.polygon.push_back(pt)

	def enclosesVertex(self, vrt):
		return self.enclosesPoint(vrt.loc)

	def enclosesPoint(self, pt):
		return Geom.isInsidePoly(self.polygon, pt)
