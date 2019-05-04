from abc import ABC, abstractmethod

from model.model_service import Model
from utils.drawing import CreateCircle
import utils.geometry as geometry

VERTEX_COLOR = "Purple"
model = Model()

class Entity(ABC):
	def __init__(self, canvas, color, name):
		self.color = color
		self.name = name
		self.canvas = canvas
		self.canvasId = None

	@abstractmethod
	def createShape(self):
		pass

class Vertex(Entity):
	def __init__(self, canvas, name, loc, ownerObs=None, color=VERTEX_COLOR, render=False):
		super().__init__(canvas = canvas, color = color, name = name)
		self.loc = loc
		self.ownerObs = ownerObs
		if (render):
			self.createShape()

	def createShape(self):
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
			intersection = o.intersection(l)
			# if vertices are visible, the intersection is either empty or it is a line segment
			# whose at least one of the end points is one of the two vertices
			if (len(intersection) == 0):
				continue
			if (len(intersection) > 1):
				return False
			if (type(intersection[0]) is Segment2D)
				... continue from here
