""" TP Canvas """
import json
import os
import tkinter as tk
import sys

from model.modelService import Model
from model.cable import Cable
from model.destination import Destination
from model.obstacle import Obstacle
from model.robot import Robot
from utils.cgal.types import Point

class Canvas(object):
	def __init__(self, master, app):
		self.window = master
		self.canvas = tk.Canvas(master = master)
		self.canvas.pack(fill=tk.BOTH, expand=True)
		self.model = Model()
		self.model.setCanvas(self.canvas)
		self.model.setApp(app)
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
				self.model.setMaxCable(float(self.parsedJson[e]))
			elif (e == 'destinations'):
				self.createDestinations(self.parsedJson[e])
			elif (e == 'obstacles'):
				self.createObstacles(self.parsedJson[e])
			else:
				sys.stderr.write('unexpected json parameter %s' % e)

	def createCableAndRobots(self, ptList):
		self.createRobots([ptList[0], ptList[-1]])
		self.model.cable.append(self.model.robots[0])
		for pt in ptList[1:-1]:
			p = Point(*[float(c) for c in pt.split(',')])
			self.model.cable.append(self.model.getVertexByLocation(p.x(), p.y()))
		self.model.cable.append(self.model.robots[-1])
		c = Cable(canvas=self.canvas, name="CABLE-O", pts=self.model.cable, isOrigin=True)
		self.model.entities[c.name] = c

	def createRobots(self, ptList):
		i = 1
		colors = ['Red', 'Blue']
		for pt in ptList:
			coords = [float(c) for c in pt.split(',')]
			r = Robot(canvas=self.canvas, color=colors[i - 1], name="R%d" % i, loc=Point(*coords))
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
		i = 0
		for obsVerts in obsArr:
			pts = [Point(*[float(c) for c in v.split(',')]) for v in obsVerts]
			o = Obstacle(canvas = self.canvas, name = 'O%s' % i, pts = pts)
			self.model.entities[o.name] = o
			self.model.obstacles.append(o)
			numVerts = len(o.vertices)
			i += 1
			for j in range(numVerts):
				v = o.vertices[j]
				prevV = o.vertices[j - 1]
				nextV = o.vertices[j + 1 if j + 1 < numVerts else 0]
				v.adjacent = [prevV, nextV]
				self.model.entities[v.name] = v
				self.model.vertices.append(v)
				self.model.addVertexByLocation(v)
