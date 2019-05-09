from abc import ABC, abstractmethod

class Entity(ABC):
	def __init__(self, canvas, color, name):
		self.color = color
		self.name = name
		self.canvas = canvas
		self.canvasId = None

	def __repr__(self):
		return "%s" % self.name

	@abstractmethod
	def createShape(self):
		pass
