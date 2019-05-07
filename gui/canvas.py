""" TP Canvas """
import json
import os
import tkinter as tk
import sys
from sympy.geometry.point import Point

from model.model_service import Model
from model.robot import Robot
from model.obstacle import Obstacle
from model.destination import Destination

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
			if (e == 'cable'):
				self.createCableAndRobots(self.parsedJson[e])
			elif (e == 'cableLength'):
				self.model.MAX_CABLE = float(self.parsedJson[e])
			elif (e == 'destinations'):
				self.createDestinations(self.parsedJson[e])
			elif (e == 'obstacles'):
				self.createObstacles(self.parsedJson[e])
			else:
				sys.stderr.write('unexpected json parameter %s' % e)

	def createCableAndRobots(self, ptList):
		self.createRobots([ptList[0], ptList[-1]])
		for pt in ptList:
			p = Point(*[float(c) for c in pt.split(',')])
			self.model.cable.append(self.model.getVertexByLocation(p.x, p.y))

	def createRobots(self, ptList):
		i = 1
		colors = ['Red', 'Blue']
		for pt in ptList:
			coords = [float(c) for c in pt.split(',')]
			r = Robot(canvas = self.canvas, color = colors[i - 1], name = "R%d" % i, loc = Point(*coords))
			self.model.entities[r.name] = r
			self.model.addVertexByLocation(r)
			self.model.robots.append(r)
			i += 1

	def createDestinations(self, ptList):
		i = 0
		for p in ptList:
			coords = [float(c) for c in p.split(',')]
			d = Destination(canvas = self.canvas, robot = self.model.robots[i], loc = Point(*coords))
			self.model.robots[i].destination = d
			self.model.entities[d.name] = d
			self.model.addVertexByLocation(d)
			i += 1

	def createObstacles(self, obsArr):
		i = 1
		for obsVerts in obsArr:
			pts = [Point(*[float(c) for c in v.split(',')]) for v in obsVerts]
			o = Obstacle(canvas = self.canvas, name = 'O%s' % i, pts = pts)
			self.model.entities[o.name] = o
			self.model.obstacles.append(o)
			for v in o.vertices:
				self.model.entities[v.name] = v
				self.model.vertices.append(v)
				self.model.addVertexByLocation(v)
			i += 1
