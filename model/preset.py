import json
import os

from model.modelService import Model
from model.cable import Cable
from model.destination import Destination
from model.obstacle import Obstacle
from model.robot import Robot
from utils.cgal.types import Point

class Preset(object):
	def __init__(self, path):
		self.model = Model(True)
		self.path = path
		self._parsedJson: dict = None
		self._build()

	def _build(self):
		if (not os.path.isfile(self.path)):
			raise FileNotFoundError("%s does not exist" % self.path)
		with open(self.path, 'r') as jsonFile:
			self._parsedJson = json.load(jsonFile)
		self._populateModel()

	def _populateModel(self):
		for e in self._parsedJson:
			if (e == 'cable'):
				self._createCableAndRobots(self._parsedJson[e])
			elif (e == 'cableLength'):
				self.model.setMaxCable(float(self._parsedJson[e]))
			elif (e == 'destinations'):
				self._createDestinations(self._parsedJson[e])
			elif (e == 'obstacles'):
				self._createObstacles(self._parsedJson[e])
			else:
				sys.stderr.write('unexpected json parameter %s' % e)

	def _createCableAndRobots(self, ptList):
		self._createRobots([ptList[0], ptList[-1]])
		self.model.cable.append(self.model.robots[0])
		for pt in ptList[1:-1]:
			p = Point(*[float(c) for c in pt.split(',')])
			self.model.cable.append(self.model.getVertexByLocation(p.x(), p.y()))
		self.model.cable.append(self.model.robots[-1])
		c = Cable(name="CABLE-O", pts=self.model.cable, isOrigin=True)
		self.model.entities[c.name] = c

	def _createRobots(self, ptList):
		i = 1
		colors = ['Red', 'Blue']
		for pt in ptList:
			coords = [float(c) for c in pt.split(',')]
			r = Robot(color=colors[i - 1], name="R%d" % i, loc=Point(*coords))
			self.model.entities[r.name] = r
			self.model.addVertexByLocation(r)
			self.model.robots.append(r)
			i += 1

	def _createDestinations(self, ptList):
		i = 0
		for p in ptList:
			coords = [float(c) for c in p.split(',')]
			d = Destination(robot=self.model.robots[i], loc=Point(*coords))
			self.model.robots[i].destination = d
			self.model.entities[d.name] = d
			self.model.addVertexByLocation(d)
			i += 1

	def _createObstacles(self, obsArr):
		i = 0
		for obsVerts in obsArr:
			pts = [Point(*[float(c) for c in v.split(',')]) for v in obsVerts]
			o = Obstacle(name='O%s' % i, pts=pts)
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
