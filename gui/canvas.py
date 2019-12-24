""" TP Canvas """
import tkinter as tk

from model.modelService import Model
from model.cable import Cable
from model.destination import Destination
from model.obstacle import Obstacle
from model.robot import Robot
from model.preset import Preset
from utils.cgal.types import Point

class Canvas(object):
	def __init__(self, master, app):
		self.window = master
		self.app = app
		self.tkCanvas = tk.Canvas(master=master)
		self.tkCanvas.pack(fill=tk.BOTH, expand=True)
		self.model: Model = None
		self.preset: Preset = None

	def buildPreset(self, jsonPath):
		self._reset()
		self.preset = Preset(jsonPath)
		self.model = self.preset.model
		self.model.setCanvas(self.tkCanvas)
		self.model.setApp(self.app)
		self._renderPreset()

	def _renderPreset(self):
		for entity in self.model.entities.values():
			entity.createShape(self)

	def renderSolution(self, finalCable):
		c1: Cable = self.model.entities["CABLE-O"]
		c1.removeShape()
		c1.createShape(self) # Bring original cable to the top
		c2 = Cable("CABLE-D", finalCable)
		self.model.entities[c2.name] = c2
		c2.createShape(self)
		print(finalCable)

	def _reset(self):
		if not self.model: return
		for entity in self.model.entities.values():
			entity.removeShape()
		self.model = None
		self.preset = None
