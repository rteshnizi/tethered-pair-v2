from .entity import Entity
from utils.drawing import CreatePolygon

OBSTACLE_COLOR = "Grey"

class Obstacle(Entity):
	def __init__(self, canvas, name, verts):
		super().__init__(canvas = canvas, color = OBSTACLE_COLOR, name = name)
		self.verts = verts
		self.createShape()

	def createShape(self):
		self.shapeId = CreatePolygon(canvas = self.canvas, pointsList = self.verts, outline = "", fill = self.color, width = 1)
