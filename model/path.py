from model.entity import Entity
from utils.cgal.drawing import CreateLine, CreateCircle, RemoveShape
from utils.vertexUtils import convertToPoint

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
		self._ptsCanvasIds = []

	def createShape(self, canvas):
		if (self.canvasId): return
		self.canvas = canvas
		self.canvasId = CreateLine(self.canvas.tkCanvas, pointsList=self.pts, color=self.color, tag=self.name, width=WIDTH, arrow=True)
		for i in range(len(self.pts)):
			pt = self.pts[i]
			canvasId = CreateCircle(self.canvas.tkCanvas, center=pt, radius=2, outline=self.color, fill=self.color, width=WIDTH, tag="%s-%d" % (self.name, i))
			self._ptsCanvasIds.append(canvasId)

	def removeShape(self):
		for ptsCanvasId in self._ptsCanvasIds:
			RemoveShape(self.canvas.tkCanvas, ptsCanvasId)
		self._ptsCanvasIds = []
		super().removeShape()
