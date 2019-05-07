from abc import ABC, abstractmethod

class Entity(ABC):
	def __init__(self, canvas, color, name):
		self.color = color
		self.name = name
		self.canvas = canvas
		self.canvasId = None

	@abstractmethod
	def createShape(self):
		pass
