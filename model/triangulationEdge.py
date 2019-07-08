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
		canvas: tk.Canvas

		color: color string

		name: str

		pts: [sympy.geometry.point.Point]
		"""
		super().__init__(canvas = canvas, color = TRIANGULATION_COLOR, name = name)
		self.pts = pts
		self.line = None
		self.createShape(pts)

	def createShape(self, pts):
		self.canvasId = CreateLine(self.canvas, pointsList = pts, color = TRIANGULATION_COLOR, dash = TRIANGULATION_DASH_PATTERN)
