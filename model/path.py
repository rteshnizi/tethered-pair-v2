from model.entity import Entity
from utils.cgal.drawing import CreateLine
from  utils.vertexUtils import convertToPoint

WIDTH = 1

class Path(Entity):
	def __init__(self, name, pts: list, color):
		"""
		params
		===

		color: color string

		name: str

		pts: A list of at least 2 utils.cgal.types.Point
		"""
		super().__init__(color=color, name=name)
		if isinstance(pts, list):
			if len(pts) < 2:
				raise RuntimeError("at least 2 Points are needed for a Path")
		self.pts = [convertToPoint(v) for v in pts]

	def createShape(self, canvas):
		if (self.canvasId): return
		self.canvas = canvas
		self.canvasId = CreateLine(self.canvas.tkCanvas, pointsList=self.pts, color=self.color, tag=self.name, width=WIDTH, arrow=True)
