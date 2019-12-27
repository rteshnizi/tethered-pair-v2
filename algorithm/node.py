from model.modelService import Model
from utils.cgal.geometry import vertexDistance

model = Model()

# TODO: Add a + and - operators to cost class so the code would be cleaner
class Cost(object):
	def __init__(self, vals=[0, 0]):
		"""
		vals: is a list of 2 numbers, the first is the cost for robot[0] and second is for robot[1]
		"""
		self.vals = vals

	def __repr__(self):
		return "(%.2f, %.2f)" % (self.vals[0], self.vals[1])

	def __getitem__(self, index):
		if index != 0 and index != 1: raise IndexError("Cost has index 0 or 1 only.")
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

class Node(object):
	"""
	The definition of a node in the planning tree
	"""
	def __init__(self, cable, parent=None, fractions=[1, 1]):
		"""

		"""
		self.cable = cable
		self.parent = parent
		self.f = Cost()
		if parent:
			self.f = Cost([parent.f[0] + vertexDistance(parent.cable[0], cable[0]), parent.f[1] + vertexDistance(parent.cable[-1], cable[-1])])
		self.h = self._calcH()
		self.g = self._calcG()
		self.children = []
		self.fractions = fractions # fractions is only defined for the two ends of the cable

	def __repr__(self):
		return "%s - %.2f" % (repr(self.cable), self.pQGetCost(self))

	def _calcH(self):
		return self._heuristic1()

	def _heuristic1(self):
		h1 = vertexDistance(self.cable[0], model.robots[0].destination)
		h2 = vertexDistance(self.cable[-1], model.robots[-1].destination)
		return Cost([h1, h2])

	def _calcG(self):
		return Cost([self.f[0] + self.h[0], self.f[1] + self.h[1]])

	@staticmethod
	def pQGetCost(n):
		"""
		Since the optimization metric is minimizing the max, this function returns the max of the two costs
		"""
		return n.g.max()[0]
