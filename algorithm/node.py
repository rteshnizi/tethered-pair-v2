from model.model_service import Model
from utils.cgal.geometry import vertexDistance

model = Model()

class Cost(object):
	def __init__(self, vals = [0, 0]):
		self.vals = vals

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

class Node(object):
	"""
	The definition of a node in the planning tree
	"""
	def __init__(self, cable, parent = None, cost = [0, 0], fractions = [1, 1]):
		self.cable = cable
		self.parent = parent
		self.f = Cost(vals = cost)
		self.h = self._calcH()
		self.g = self._calcG()
		self.children = []
		self.fractions = fractions # fractions is only defined for the two ends of the cable

	def estimate(self):
		return cost + self.heuristic()

	def _calcH(self):
		return self._heuristic1()

	def _heuristic1(self):
		h1 = vertexDistance(self.cable[0], model.robots[0].destination)
		h2 = vertexDistance(self.cable[-1], model.robots[-1].destination)
		return Cost(vals = [h1, h2])

	def _calcG(self):
		return Cost(vals = [self.f.vals[0] + self.h.vals[0], self.f.vals[1] + self.h.vals[1]])

	@staticmethod
	def pQGetCost(n):
		"""
		Since the optimization metric is minimizing the max, this function returns the max of the two costs
		"""
		return n.g.max()[0]
