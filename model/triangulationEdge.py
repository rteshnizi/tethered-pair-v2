from model.entity import Entity
from model.modelService import Model
from model.vertex import Vertex
from utils.cgal.drawing import CreateLine
from utils.cgal.types import Segment

TRIANGULATION_COLOR = "Black"
TRIANGULATION_CONSTRAINT_COLOR = "Red"
TRIANGULATION_DASH_PATTERN = (3, 3)
model = Model()

class TriangulationEdge(Entity):
	def __init__(self, canvas, name, pts, isConstraint=False):
		"""
		The shape is not created by default.

		params
		===

		canvas: tk.Canvas

		color: color string

		name: str

		pts: A list of 2 utils.cgal.types.Point or a utils.cgal.types.Segment
		"""
		super().__init__(canvas=canvas, color=TRIANGULATION_CONSTRAINT_COLOR if isConstraint else TRIANGULATION_COLOR, name=name)
		if isinstance(pts, list):
			if len(pts) != 2:
				raise RuntimeError("2 Points are needed for a Triangulation Edge")
			self.pts = pts
			self.line = Segment(pts[0], pts[1])
		else:
			self.pts = [pts.source(), pts.target()]
			self.line = pts

	def createShape(self):
		if (self.canvasId): return
		self.canvasId = CreateLine(self.canvas, pointsList=self.pts, color=self.color, tag=self.name, dash=TRIANGULATION_DASH_PATTERN)
		# model.entities[self.name] = self

	def highlightEdge(self):
		self.removeShape()
		self.canvasId = CreateLine(self.canvas, pointsList=self.pts, color=self.color, tag=self.name, width=3, dash=TRIANGULATION_DASH_PATTERN)
