from abc import ABC, abstractmethod

from utils.drawing import CreateCircle

VERTEX_COLOR = "Purple"

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
	def __init__(self, canvas, name, loc, color=VERTEX_COLOR, render=False):
		super().__init__(canvas = canvas, color = color, name = name)
		self.loc = loc
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
