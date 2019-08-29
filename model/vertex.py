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
	def __init__(self, canvas, name, loc, ownerObs=None, color=VERTEX_COLOR, render=False):
		super().__init__(canvas=canvas, color=color, name=name)
		self.loc = loc
		self.ownerObs = ownerObs
		self.adjacent = []
		self.gaps = []
		if (render):
			self.createShape()

	def createShape(self):
		if (self.canvasId): return
		self.canvasId = CreateCircle(
			canvas=self.canvas,
			center=self.loc,
			radius=2,
			outline=self.color,
			fill="",
			width=1,
			tag=self.name
		)

	def isVisible(self, other):
		l = Segment(self.loc, other.loc)
		for o in model.obstacles:
			intersections = o.intersection(l)
			# if vertices are visible, the intersection is either empty or it is a line segment
			# whose at least one of the end points is one of the two vertices
			if (len(intersections) == 0):
				continue
			# If obstacles are concave, we might have more than 2 intersections
			for intersection in intersections:
				if isinstance(intersection, Point):
					if not (intersection == self.loc or intersection == other.loc):
						return False
				else: # intersection is a Segment
					# Segments show that an edge is tangent to the visibility ray
					# They don't block visibility
					pass
		return True
