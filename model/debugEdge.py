from model.entity import Entity
from model.modelService import Model
from model.vertex import Vertex
from utils.cgal.drawing import CreateLine
from utils.cgal.types import Segment

COLOR = "Black"
SECONDARY_COLOR = "Red"
DASH_PATTERN = (3, 3)
model = Model()

class DebugEdge(Entity):
	def __init__(self, name, pts, isConstraint=False, isDirected=False):
		"""
		The shape is not created by default.

		params
		===

		canvas: Canvas object (not tk.Canvas)

		color: color string

		name: str

		pts: A list of 2 utils.cgal.types.Point or a utils.cgal.types.Segment
		"""
		super().__init__(color=SECONDARY_COLOR if isConstraint else COLOR, name=name)
		if isinstance(pts, list):
			if len(pts) != 2:
				raise RuntimeError("2 Points are needed for a Triangulation Edge")
			self.pts = pts
			self.line = Segment(pts[0], pts[1])
		elif isinstance(pts, Segment):
			self.pts = [pts.source(), pts.target()]
			self.line = pts
		else:
			raise TypeError("pts should either be a list of points or a CGAL Segment")
		self.isDirected = isDirected

	def createShape(self, canvas):
		if (self.canvasId): return
		self.canvas = canvas
		self.canvasId = CreateLine(self.canvas.tkCanvas, pointsList=self.pts, color=self.color, tag=self.name, dash=DASH_PATTERN, arrow=self.isDirected)

	def highlightEdge(self, canvas):
		self.removeShape()
		self.canvas = canvas
		self.canvasId = CreateLine(self.canvas.tkCanvas, pointsList=self.pts, color=self.color, tag=self.name, width=3, dash=DASH_PATTERN, arrow=self.isDirected)
