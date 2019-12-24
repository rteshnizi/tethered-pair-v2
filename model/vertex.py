import utils.cgal.geometry as Geom
from model.modelService import Model
from model.entity import Entity
from utils.cgal.drawing import CreateCircle
from utils.cgal.types import Point, Segment

VERTEX_COLOR = "Purple"
model = Model()

class Vertex(Entity):
	"""
	Props:
	===

	loc: Point

	ownerObs: Obstacle that this vertex is on

	adjacent: list The two other vertices of the owner obstacle, adjacent to this vertex

	gaps: list of the vertices adjacent to this vertex on the reduced visibility graph
	"""
	def __init__(self, name, loc, ownerObs=None, color=VERTEX_COLOR):
		super().__init__(color=color, name=name)
		self.loc = loc
		self.ownerObs = ownerObs
		self.adjacent = []
		self.gaps = []

	def createShape(self, canvas):
		if (self.canvasId): return
		self.canvas = canvas
		self.canvasId = CreateCircle(
			canvas=self.canvas.tkCanvas,
			center=self.loc,
			radius=2,
			outline=self.color,
			fill="",
			width=1,
			tag=self.name
		)

	def isVisible(self, other):
		return Geom.isVisible(self, other)
