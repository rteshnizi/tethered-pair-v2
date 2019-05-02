""" TP Canvas """
import json
import os
import tkinter as tk
import sys
from sympy.geometry.point import Point

from model.model_service import Model
from model.robot import Robot
from model.obstacle import Obstacle

class Canvas(object):
	def __init__(self, master):
		self.window = master
		self.canvas = tk.Canvas(master = master)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		self.model = Model()
		self.parsedJson = None

	def parseJson(self, jsonPath):
		if (not os.path.isfile(jsonPath)):
			return
		with open(jsonPath, 'r') as jsonFile:
			self.parsedJson = json.load(jsonFile)
		self.createEntities()

	def createEntities(self):
		for e in self.parsedJson:
			if (e == 'robots'):
				self.createRobots(self.parsedJson[e])
			elif (e == 'destinations'):
				self.createDestinations(self.parsedJson[e])
			elif (e == 'obstacles'):
				self.createObstacles(self.parsedJson[e])
			elif (e == 'cableLength'):
				self.model.MAX_CABLE = float(self.parsedJson[e])
			else:
				sys.stderr.write('unexpected json parameter %s' % e)

	def createRobots(self, json):
		i = 1
		colors = ['Red', 'Blue']
		for p in json:
			coords = [float(c) for c in p.split(',')]
			r = Robot(canvas = self.canvas, color = colors[i - 1], name = "R%d" % i, loc = Point(*coords))
			self.model.entities.append(r)
			self.model.robots.append(r)
			i += 1

	def createDestinations(self, json):
		i = 0
		for p in json:
			coords = [float(c) for c in p.split(',')]
			self.model.robots[i].setDestination(Point(*coords))
			i += 1

	def createObstacles(self, json):
		i = 1
		for obsVerts in json:
			verts = [Point(*[float(c) for c in v.split(',')]) for v in obsVerts]
			for v in verts:
				self.model.vertices.append(v)
			o = Obstacle(canvas = self.canvas, name = 'O%s' % i, verts = verts)
			self.model.entities.append(o)
			self.model.obstacles.append(o)
			i += 1
