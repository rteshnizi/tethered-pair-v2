from model.vertex import Vertex
from utils.cgal.drawing import CreateCircle

DESTINATION_RADIUS = 5

class Destination(Vertex):
	def __init__(self, canvas, robot, loc):
		"""
		canvas: tk.Canvas

		robot: the owner Robot instance

		loc: utils.cgal.types.Point
		"""
		super().__init__(canvas=canvas, color=robot.color, name=robot.name.replace('R', 'D'), loc=loc)
		self.robot = robot

	def createShape(self):
		if (self.canvasId): return
		self.canvasId = CreateCircle(
			canvas=self.canvas,
			center=self.loc,
			radius=DESTINATION_RADIUS,
			outline=self.color,
			fill="",
			width=1,
			tag=self.name
		)
