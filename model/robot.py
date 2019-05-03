from .entity import PointEntity
from utils.drawing import CreateCircle

ROBOT_RADIUS = 5
ROBOT_WIDTH = 2

class Robot(PointEntity):
	def __init__(self, canvas, color, name, loc):
		"""
		canvas: tk.Canvas

		color: color string

		name: str

		loc: sympy.geometry.point.Point
		"""

		super().__init__(canvas = canvas, color = color, name = name, loc = loc)
		self.destination = None
		self.destinationShapeId = None
		self.createShape()

	def createShape(self):
		self.canvasId = CreateCircle(
			canvas = self.canvas,
			center = self.loc,
			radius = ROBOT_RADIUS,
			outline = "",
			fill = self.color,
			width = 1
		)

	def setDestination(self, d):
		"""
		d: sympy.geometry.point.Point
		"""
		self.destination = d
		self.destinationShapeId = CreateCircle(
			canvas = self.canvas,
			center = self.destination,
			radius = ROBOT_RADIUS,
			outline = self.color,
			fill = "",
			width = 1
		)
