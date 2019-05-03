from abc import ABC, abstractmethod

class Entity(ABC):
	def __init__(self, canvas, color, name):
		self.color = color
		self.name = name
		self.canvas = canvas
		self.canvasId = -1

	@abstractmethod
	def createShape(self):
		pass

class PointEntity(Entity):
	def __init__(self, canvas, color, name, loc):
		super().__init__(canvas = canvas, color = color, name = name)
		self.loc = loc
