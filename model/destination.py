from model.vertex import Vertex
from utils.cgal.drawing import CreateCircle

DESTINATION_RADIUS = 5

class Destination(Vertex):
	def __init__(self, robot, loc):
		"""
		canvas: tk.Canvas

		robot: the owner Robot instance

		loc: utils.cgal.types.Point
		"""
		super().__init__(color=robot.color, name=robot.name.replace('R', 'D'), loc=loc)
		self.robot = robot

	def createShape(self, canvas):
		if (self.canvasId): return
		self.canvas = canvas
		self.canvasId = CreateCircle(
			canvas=self.canvas.tkCanvas,
			center=self.loc,
			radius=DESTINATION_RADIUS,
			outline=self.color,
			fill="",
			width=1,
			tag=self.name
		)
