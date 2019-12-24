from abc import ABC, abstractmethod

from utils.cgal.drawing import RemoveShape

class Entity(ABC):
	def __init__(self, color, name):
		self.color = color
		self.name = name
		self.canvas = None
		self.canvasId = None

	def __repr__(self):
		return "%s" % self.name

	def removeShape(self):
		if (self.canvasId):
			RemoveShape(self.canvas.tkCanvas, self.canvasId)
			self.canvasId = None
			self.canvas = None

	@abstractmethod
	def createShape(self, canvas):
		pass
