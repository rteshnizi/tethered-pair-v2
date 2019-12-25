from model.entity import Entity
from utils.cgal.drawing import CreateLine
from  utils.vertexUtils import convertToPoint

WIDTH = 3
CABLE_ORIGIN_COLOR = "Green"
CABLE_FINAL_COLOR = "DarkRed"

class Cable(Entity):
	def __init__(self, name, pts: list, isOrigin=False):
		"""
		params
		===

		color: color string

		name: str

		pts: A list of at least 2 utils.cgal.types.Point
		"""
		super().__init__(color=CABLE_ORIGIN_COLOR if isOrigin else CABLE_FINAL_COLOR, name=name)
		if isinstance(pts, list):
			if len(pts) < 2:
				raise RuntimeError("at least 2 Points are needed for a Cable")
		# for cable we draw a polygon just so we have a single id instead of a group of IDs for line segments
		self.pts = [convertToPoint(v) for v in pts]

	def createShape(self, canvas):
		if (self.canvasId): return
		self.canvas = canvas
		self.canvasId = CreateLine(self.canvas.tkCanvas, pointsList=self.pts, color=self.color, tag=self.name, width=WIDTH)
