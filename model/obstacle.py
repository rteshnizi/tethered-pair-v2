from .entity import Entity
from utils.drawing import CreatePolygon
from sympy.geometry.polygon import Polygon

OBSTACLE_COLOR = "Grey"

class Obstacle(Entity):
	def __init__(self, canvas, name, verts):
		"""
		canvas: tk.Canvas

		color: color string

		name: str

		verts: [sympy.geometry.point.Point]
		"""
		super().__init__(canvas = canvas, color = OBSTACLE_COLOR, name = name)
		self.verts = verts
		self.polygon = None
		self.createShape()

	def createShape(self):
		self.canvasId = CreatePolygon(canvas = self.canvas, pointsList = self.verts, outline = "", fill = self.color, width = 1)
		self.polygon = Polygon(*self.verts)
