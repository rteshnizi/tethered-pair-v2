from model.model_service import Model
from model.entity import Entity
from utils.cgal.drawing import CreateCircle
import utils.cgal.geometry as geometry

VERTEX_COLOR = "Purple"
model = Model()

class Vertex(Entity):
	def __init__(self, canvas, name, loc, ownerObs=None, color=VERTEX_COLOR, render=False):
		super().__init__(canvas = canvas, color = color, name = name)
		self.loc = loc
		self.ownerObs = ownerObs
		self.adjacent = []
		if (render):
			self.createShape()

	def createShape(self):
		if (self.canvasId): return
		self.canvasId = CreateCircle(
			canvas = self.canvas,
			center = self.loc,
			radius = 2,
			outline = self.color,
			fill = "",
			width = 1
		)

	def isVisible(self, other):
		l = geometry.createSegmentFromVertices(self, other)
		for o in model.obstacles:
			intersections = o.intersection(l)
			# if vertices are visible, the intersection is either empty or it is a line segment
			# whose at least one of the end points is one of the two vertices
			if (len(intersections) == 0):
				continue
			# If obstacles are concave, we might have more than 2 intersections
			for intersection in intersections:
				if (isinstance(intersection, Point)):
					if (not (intersection.equals(self.loc) or intersection.equals(other.loc))):
						return False
				else: # intersection is a Segment
					# Segments show that an edge is tangent to the visibility ray
					# They don't block visibility
					pass
		return True
