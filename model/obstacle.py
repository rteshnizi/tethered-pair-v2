from sympy.geometry.polygon import Polygon

from model.entity import Entity
from model.model_service import Model
from model.vertex import Vertex
from utils.drawing import CreatePolygon

OBSTACLE_COLOR = "Grey"
mode = Model()

class Obstacle(Entity):
	def __init__(self, canvas, name, pts):
		"""
		canvas: tk.Canvas

		color: color string

		name: str

		pts: [sympy.geometry.point.Point]
		"""
		super().__init__(canvas = canvas, color = OBSTACLE_COLOR, name = name)
		self.vertices = []
		self.polygon = None
		self.createVertices(pts)
		self.createShape(pts)

	def createVertices(self, pts):
		for i in range(0, len(pts)):
			v = Vertex(canvas = self.canvas, name="%s-%d" % (self.name, i), loc = pts[i], ownerObs=self, render = True)
			self.vertices.append(v)

	def createShape(self, pts):
		if (self.canvasId): return
		self.canvasId = CreatePolygon(canvas = self.canvas, pointsList = pts, outline = "", fill = self.color, width = 1)
		self.polygon = Polygon(*pts)
