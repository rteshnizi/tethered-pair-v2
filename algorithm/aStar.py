from sympy.geometry.polygon import Polygon

from algorithm.gap import gapDetector
from algorithm.node import Node
from model.model_service import Model
import utils.geometry as geometry
from utils.priorityQ import PriorityQ

model = Model()

def aStar():
	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	while (not q.isEmpty()):
		n = q.dequeue()
		if (isAtDestination(n)):
			return # For now terminate at first solution
		V_A = gapDetector(n.cable[0], model.robots[0])
		V_B = gapDetector(n.cable[-1], model.robots[-1])
		for va in V_A:
			for vb in V_B:
				c = tightenCable(n.cable, va.vrt, vb.vrt)
				if (len(c) == 0):
					continue


def isAtDestination(n):
	return n.cable[0].name == model.robots[0].destination.name and n.cable[-1].name == model.robots[-1].destination.name

def tightenCable(cable, va, vb):
	# polygon = Polygon([va.loc] + [v.loc for v in cable] + [v_b.loc])
	sidesA = [True] + getSides(cable, va, +1) + [True]
	sidesB = [True] + getSides(cable, vb, -1) + [True]
	newCable = [va] + cable + [vb]
	bound = len(newCable) - 1
	i = 0
	while (i < bound):
		v1 = newCable[i - 1]
		v2 = newCable[i]
		v3 = newCable[i + 1]
		if (sidesA[i]):
			inner = geometry.getInnerVertices(v1, v2, v3)
			hull = geometry.getConvexHull(inner + [v1, v3])
			newCable = newCable[:i] + hull + newCable[i + 1:]
			bound = len(newCable) - 1
		i += 1
	i = len(newCable) - 2
	while (i > 0):
		v1 = newCable[i + 1]
		v2 = newCable[i]
		v3 = newCable[i - 1]
		if (sidesB[i]):
			inner = geometry.getInnerVertices(v1, v2, v3)
			hull = geometry.getConvexHull(inner + [v1, v3])
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

def getSide(cableVert, robot, dest):
	if (len(cableVert.adjacent) == 0):
		sides[i] = True
	else:
		c = geometry.cross(cableVert.loc, cableVert.adjacent[0].loc)
		sides[i] = True if c * vCross > 0 else False # cableVert and v are on the same side of the cable
	return sides
