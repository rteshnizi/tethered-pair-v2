from math import inf
from functools import partial
from model.modelService import Model
from utils.cgal.geometry import vertexDistance, convertToPoint
from utils.priorityQ import PriorityQ
from utils.logger import Logger

logger = Logger()
model = Model()
INFINITY_COST = inf

# TODO: Add a + and - operators to cost class so the code would be cleaner
class Cost(object):
	def __init__(self, vals=[INFINITY_COST, INFINITY_COST]):
		"""
		vals: is a list of 2 numbers, the first is the cost for robot[0] and second is for robot[1]
		"""
		self.vals = vals

	def __repr__(self):
		c1 = ("%.2f" % self.vals[0]).ljust(7)
		return "(%s, %.2f)" % (c1, self.vals[1])

	def __getitem__(self, index):
		if index != 0 and index != 1 and index != -1: raise IndexError("Cost has index 0 or 1 or -1 only.")
		return self.vals[index]

	def min(self):
		"""
		Return min cost along with its index in a list.
		"""
		if (self.vals[0] < self.vals[1]):
			return (self.vals[0], 0)
		return (self.vals[1], 1)

	def max(self):
		"""
		Return min cost along with its index in a list.
		"""
		if (self.vals[0] >= self.vals[1]):
			return (self.vals[0], 0)
		return (self.vals[1], 1)

class _SimpleNode(object):
	def __init__(self, vert, h, parent: "_SimpleNode"):
		self.vert = vert
		self.parent = parent
		self.g = vertexDistance(self.vert, self.parent.vert) + self.parent.g if self.parent else 0
		self.h = h
		self.f = self.h + self.g

	def __repr__(self):
		return "%s - %.2f" % (repr(self.vert), self.f)

class Node(object):
	"""
	The definition of a node in the planning tree
	"""
	def __init__(self, cable, parent: "Node", debug=False, heuristicFuncName="_heuristicShortestPath", fractions=[1, 1]):
		self.cable = cable
		self.g = Cost()
		self.h = Cost()
		self.f = Cost()
		self.debug = debug
		self.parent: "Node" = None
		self.heuristicFuncName = heuristicFuncName
		self._heuristic = getattr(self, self.heuristicFuncName)
		# self._heuristic = self._heuristicTrmpp
		self.updateParent(parent)
		self.fractions = fractions # fractions is only defined for the two ends of the cable

	def __repr__(self):
		return "%s - %s" % (repr(self.cable), repr(self.f))

	def _calcH(self) -> Cost:
		return self._heuristic()

	def _heuristicTrmpp(self) -> Cost:
		root = Node(cable=self.cable, parent=None, debug=self.debug, heuristicFuncName=self.heuristicFuncName)
		solution = _privateAStar(root=root, MAX_CABLE=model.MAX_CABLE * (len(self.cable) + 1) * 1.25, debug=self.debug)
		model.solution.expanded += solution.expanded
		model.solution.genereted += solution.genereted
		if self.debug: logger.log("T = %.2f" % solution.time)
		if not solution.content:
			return Cost()
		return solution.content.cost

	def _heuristicShortestPath(self) -> Cost:
		h1 = self._aStar(0).g
		h2 = self._aStar(-1).g
		return Cost([h1, h2])

	def _heuristicLineDist(self) -> Cost:
		h1 = vertexDistance(self.cable[0], model.robots[0].destination)
		h2 = vertexDistance(self.cable[-1], model.robots[1].destination)
		return Cost([h1, h2])

	def _heuristicNone(self) -> Cost:
		return Cost([0, 0])

	def _calcF(self) -> Cost:
		return Cost([self.g[0] + self.h[0], self.g[1] + self.h[1]])

	def _getPath(self, leftSide: bool):
		path = []
		node = self
		while node:
			path.append(node.cable[0 if leftSide else -1])
			node = node.parent
		return path[::-1]

	def _aStar(self, index) -> "_SimpleNode":
		orig = self.cable[index]
		dest = model.robots[index].destination
		hFunc = lambda v: vertexDistance(v, dest)
		nodeMap = {} # We keep a map of nodes here to update their child-parent relationship
		q = PriorityQ(key1=lambda n: n.f, key2=lambda n: 0) # The Priority Queue container
		root = _SimpleNode(orig, hFunc(orig), None)
		q.enqueue(root)
		while not q.isEmpty():
			n = q.dequeue()
			if convertToPoint(n.vert) == convertToPoint(dest):
				return n
			for v in n.vert.gaps:
				child = _SimpleNode(v, hFunc(v), n)
				if v.name in nodeMap:
					if child.f < nodeMap[v.name].f:
						nodeMap[v.name] = child
				else:
					q.enqueue(child)
					nodeMap[v.name] = child
		return None

	def getPaths(self) -> list:
		paths = [self._getPath(True), self._getPath(False)]
		return paths

	def updateParent(self, newParent: "Node") -> None:
		if newParent:
			g0 = newParent.g[0] + vertexDistance(newParent.cable[0], self.cable[0])
			g1 = newParent.g[1] + vertexDistance(newParent.cable[-1], self.cable[-1])
			tentativeCost = Cost([g0, g1])
			if tentativeCost.max()[0] < self.g.max()[0]:
				self.parent = newParent
				self.g = tentativeCost
				self.parent = newParent
		else:
			self.g = Cost([0, 0])
		self.h = self._calcH()
		self.f = self._calcF()

	@staticmethod
	def pQGetPrimaryCost(n):
		"""
		Since the optimization metric is minimizing the max, this function returns the max of the two costs
		"""
		return n.f.max()[0]

	@staticmethod
	def pQGetSecondaryCost(n):
		"""
		Since the optimization metric is minimizing the max, this function returns the max of the two costs
		"""
		return n.f.min()[0]

import utils.cgal.geometry as Geom
from math import fabs, nan, isnan
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.node import Node
from algorithm.cable import tightenCable, getLongCable
from model.vertex import Vertex
from utils.cgal.types import Polygon
from algorithm.solutionLog import Solution, SolutionLog

def _privateAStar(root: Node, MAX_CABLE: int, debug=False) -> SolutionLog:
	if debug: logger.log("_privateAStar: root = %s, MAX = %d" % (root, MAX_CABLE))
	solutionLog = SolutionLog(root.heuristicFuncName)
	nodeMap = {} # We keep a map of nodes here to update their child-parent relationship
	q = PriorityQ(key1=Node.pQGetPrimaryCost, key2=Node.pQGetSecondaryCost) # The Priority Queue container
	q.enqueue(root)
	count = 0
	destinationsFound = 0
	while not q.isEmpty():
		n: Node = q.dequeue()
		count += 1
		# visited.add(n)
		if isAtDestination(n):
			solutionLog.content = Solution.createFromNode(n)
			solutionLog.expanded = count
			solutionLog.genereted = len(nodeMap)
			destinationsFound += 1
			return solutionLog
		# Va = n.cable[0].gaps if n.fractions[0] == 1 else {n.cable[0]}
		Va = n.cable[0].gaps if n.cable[0].name != "D1" else {n.cable[0]}
		for va in Va:
			if isUndoingLastMove(n, va, 0): continue
			# Vb = n.cable[-1].gaps if n.fractions[1] == 1 else {n.cable[-1]}
			Vb = n.cable[-1].gaps if n.cable[-1].name != "D2" else {n.cable[-1]}
			for vb in Vb:
				if isUndoingLastMove(n, vb, -1): continue
				if areBothStaying(n, va, vb): continue
				# For now I deliberately avoid cross movement because it crashes the triangulation
				# In reality we can fix this by mirorring the space (like I did in the previous paper)
				if isThereCrossMovement(n.cable, va, vb): continue
				newCable = None
				# FIXME: Defensively ignoring exceptions
				try:
					newCable = tightenCable(n.cable, va, vb)
				except:
					continue
				l = Geom.lengthOfCurve(newCable)
				if l <= MAX_CABLE:
					addChildNode(newCable, n, nodeMap, q, False)
	solutionLog.expanded = count
	solutionLog.genereted = len(nodeMap)
	solutionLog.setEndTime()
	return solutionLog

def isUndoingLastMove(node, v, index):
	if not node.parent: return False
	if v.name == "D1" or v.name == "D2": return False
	if convertToPoint(node.parent.cable[index]) != convertToPoint(v): return False
	path = node._getPath(index  == 0)
	path = removeRepeatedVertsOrdered(path)
	if convertToPoint(node.parent.cable[-2]) != convertToPoint(v): return False
	return True

def areBothStaying(parent, va, vb):
	if convertToPoint(parent.cable[0]) != convertToPoint(va): return False
	if convertToPoint(parent.cable[-1]) != convertToPoint(vb): return False
	return True

def isThereCrossMovement(cable, dest1, dest2):
	# I've also included the case where the polygon is not simple
	cable = getLongCable(cable, dest1, dest2)
	cable = removeRepeatedVertsOrdered(cable)
	if len(cable) < 3: return False
	p = Polygon([convertToPoint(v) for v in cable])
	return not p.is_simple()

def isAtDestination(n) -> bool:
	if not n: return False
	return convertToPoint(n.cable[0]) == convertToPoint(model.robots[0].destination) and convertToPoint(n.cable[-1]) == convertToPoint(model.robots[1].destination)

def getCableId(cable, fractions) -> str:
	# return "%s-[%.6f, %.6f]" % (repr(cable), fractions[0], fractions[1])
	return repr(cable)

def addChildNode(newCable, parent, nodeMap, pQ, debug, fractions=[1, 1]) -> None:
	cableStr = getCableId(newCable, fractions)
	if cableStr in nodeMap:
		nodeMap[cableStr].updateParent(parent)
		if debug: logger.log("UPDATE %s @ %s" % (repr(nodeMap[cableStr].f), cableStr))
	else:
		child = Node(cable=newCable, parent=parent, debug=parent.debug, heuristicFuncName="_heuristicShortestPath")
		if debug: logger.log("ADDING %s @ %s" % (repr(child.f), cableStr))
		nodeMap[cableStr] = child
		pQ.enqueue(child)
