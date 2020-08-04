""" TP Canvas """
import tkinter as tk

from algorithm.solutionLog import SolutionLog
from model.modelService import Model
from model.cable import Cable
from model.destination import Destination
from model.obstacle import Obstacle
from model.robot import Robot
from model.preset import Preset
from model.path import Path
from utils.cgal.types import Point
import utils.cgal.geometry as Geom
from utils.logger import Logger

logger = Logger()

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
		self.model.setCanvas(self)
		self.model.setApp(self.app)
		self._renderPreset()

	def _reset(self):
		if not self.model: return
		for entity in self.model.entities.values():
			entity.removeShape()
		self.model = None
		self.preset = None

	def _renderPreset(self):
		for entity in self.model.entities.values():
			entity.createShape(self)

	def _renderCable(self, cable):
		""" Used in testing Tighten algorithm. """
		# Bring original cable to the top
		c1: Cable = self.model.entities["CABLE-O"]
		c1.removeShape()
		c1.createShape(self)
		# Create final cable configuration
		c2 = Cable("CABLE-D", cable)
		self.model.entities[c2.name] = c2
		c2.createShape(self)
		print("CABLE-D", cable, "(%.2f)" % Geom.lengthOfCurve(cable))

	def _renderPaths(self, paths):
		print("paths:", paths)
		path = Path("P1", paths[0], self.model.robots[0].color)
		self.model.entities[path.name] = path
		path.createShape(self)
		path = Path("P2", paths[1], self.model.robots[1].color)
		self.model.entities[path.name] = path
		path.createShape(self)

	def renderSolution(self, solution: SolutionLog, debug=False):
		logger.log("T = %.2f" % solution.time)
		if not solution.content:
			print("NO SOLUTIONS")
			return
		self._renderCable(solution.content.cable)
		self._renderPaths(solution.content.paths)
