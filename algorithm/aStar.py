from sympy.geometry import Polygon

from algorithm.gap import gapDetector
import utils.geometry as geometry
from model.model_service import Model
from algorithm.node import Node
from utils.priorityQ import PriorityQ
from utils.triangulation import triangulate

model = Model()

def aStar():
	triangulate([model.cable[0], model.cable[-1], model.robots[-1].destination, model.robots[0].destination])
	reza = 0
	# q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	# root = Node(cable=model.cable)
	# q.enqueue(root)
	# while (not q.isEmpty()):
	# 	n = q.dequeue()
	# 	if (isAtDestination(n)):
	# 		return # For now terminate at first solution
	# 	V_A = gapDetector(n.cable[0], model.robots[0])
	# 	V_B = gapDetector(n.cable[-1], model.robots[-1])
	# 	for va in V_A:
	# 		for vb in V_B:
	# 			newCable = tightenCable(n.cable, va.vrt, +1)
	# 			newCable = tightenCable(newCable, vb.vrt, -1)
	# 			if (not newCable):
	# 				continue


def isAtDestination(n):
	return n.cable[0].name == model.robots[0].destination.name and n.cable[-1].name == model.robots[-1].destination.name

def tightenCable(cable, dest, direction):
	robotsInd = 0 if direction == +1 else -1
	otherEnd = -1 if direction == +1 else 0
	# First determine which side of the cable is the destination
	mainSide = getSide(dest, cable[robotsInd], cable[robotsInd + direction])
	# Then walk the cable and for every vertex on the opposite side tighten the cable
	newCable = [dest] + cable if direction == +1 else cable + [dest]
	i = robotsInd + direction
	while (cable[i].name != cable[otherEnd].name):
		v1 = newCable[i - 1]
		v2 = newCable[i]
		v3 = newCable[i + 1]
		if ((not v2.adjacent) or getSide(v2.adjacent[0], v2, v3)):
			inner = geometry.getInnerVertices(v1, v2, v3)
			hull = geometry.getConvexHullFromVertex(inner + [v1, v3])
			newCable = newCable[:i] + hull + newCable[i + 1:]
			bound = len(newCable) - 1
		i += 1
	return newCable

def getSides(cable, v, direction):
	"""
	Detect which side a cable vertex is residing with respect to the destination v and the direction of moving on the cable

	Returns a list of booleans, true means vertex is on the outside and thus can be popped
	"""
	nCable = len(cable)
	if (nCable < 3): # 2 is the min cable (the two robots)
		return [True, True]
	i = 0 if direction == +1 else -1
	end = nCable if direction == +1 else (-1 * nCable) - 1
	sides = [None] * nCable
	vCross = geometry.cross(cable[i].loc, v.loc)
	while (i != end):
		vert = cable[i]
		if (len(vert.adjacent) == 0):
			sides[i] = True
		else:
			c = geometry.cross(vert.loc, vert.adjacent[0].loc)
			sides[i] = True if c * vCross > 0 else False # vert and v are on the same side of the cable
		i += direction
	return sides

def getSide(noneCableVert, commonVert, otherCableVert):
	vec1 = noneCableVert.loc - commonVert.loc
	vec2 = otherCableVert.loc - commonVert.loc
	c = geometry.cross(vec1, vec2)
	side = True if c > 0 else False
	return side
