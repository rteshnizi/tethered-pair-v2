from model.vertex import Vertex
from utils.cgal.drawing import CreateCircle

ROBOT_RADIUS = 5
ROBOT_WIDTH = 2

class Robot(Vertex):
	def __init__(self, canvas, color, name, loc):
		"""
		canvas: tk.Canvas

		color: color string

		name: str

		loc: utils.cgal.types.Point
		"""

		super().__init__(canvas=canvas, color=color, name=name, loc=loc)
		self.destination = None

	def createShape(self):
		if (self.canvasId): return
		self.canvasId = CreateCircle(
			canvas=self.canvas,
			center=self.loc,
			radius=ROBOT_RADIUS,
			outline="",
			fill=self.color,
			width=1,
			tag=self.name
		)
