from sympy.geometry.polygon import Polygon

from model.entity import Entity
from model.model_service import Model
from model.vertex import Vertex
from utils.drawing import CreateLine

TRIANGULATION_COLOR = "Black"
TRIANGULATION_DASH_PATTERN = (2, 2)
mode = Model()

class TriangulationEdge(Entity):
	def __init__(self, canvas, name, pts):
		"""
		The shape is not created by default.

		params
		===

		canvas: tk.Canvas

		color: color string

		name: str

		pts: [sympy.geometry.point.Point]
		"""
		super().__init__(canvas = canvas, color = TRIANGULATION_COLOR, name = name)
		self.pts = pts
		self.line = None
		# Computational Geometry book pp. 52
		self.helper = None

	def createShape(self):
		if (self.canvasId): return
		self.canvasId = CreateLine(self.canvas, pointsList = self.pts, color = TRIANGULATION_COLOR, dash = TRIANGULATION_DASH_PATTERN)
