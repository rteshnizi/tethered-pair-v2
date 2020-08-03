from math import inf
from model.modelService import Model
from utils.cgal.geometry import vertexDistance, convertToPoint
from utils.priorityQ import PriorityQ
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
	def __init__(self, cable, parent: "Node", heuristicFunc=self._heuristicAStarDist, fractions=[1, 1]):
		self.cable = cable
		self.g = Cost()
		self.h = Cost()
		self.f = Cost()
		self.parent: "Node" = None
		self.updateParent(parent)
		self.fractions = fractions # fractions is only defined for the two ends of the cable
		self._heuristic = heuristicFunc

	def __repr__(self):
		return "%s - %s" % (repr(self.cable), repr(self.f))

	def _calcH(self) -> Cost:
		return self._heuristic()

	def _heuristicAStarDist(self) -> Cost:
		h1 = self._aStar(0).g
		h2 = self._aStar(-1).g
		return Cost([h1, h2])

	def _heuristicEuclideanDist(self) -> Cost:
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
