from abc import ABC, abstractmethod

from utils.drawing import RemoveShape

class Entity(ABC):
	def __init__(self, canvas, color, name):
		self.color = color
		self.name = name
		self.canvas = canvas
		self.canvasId = None

	def __repr__(self):
		return "%s" % self.name

	def removeShape(self):
		if (self.canvasId):
			RemoveShape(self.canvas, self.canvasId)
			self.canvasId = None

	@abstractmethod
	def createShape(self):
		pass
