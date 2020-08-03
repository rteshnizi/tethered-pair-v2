from timeit import default_timer as timer
from algorithm.node import Cost, Node

class Solution:
	def createFromNode(node: Node):
		return Solution(node.cable, node.getPaths(), node.g)

	def __init__(self, cable, paths, cost: Cost):
		self.cable = cable
		self.paths = paths
		self.cost = cost

class SolutionLog:
	def __init__(self, maxCable: int = 0):
		self._content: Solution = None
		self.maxCable = maxCable
		self.expanded = 0
		self.genereted = 0
		self._startTime = timer()
		self._endTime = 0.0
		self._time = -1

	@property
	def content(self) -> Solution:
		return self._content

	@content.setter
	def content(self, value: Solution):
		if self.content:
			raise RuntimeError("Content can only be set once.")
		self._endTime = timer()
		self._content = value

	@property
	def time(self):
		if self._time < 0:
			return self._endTime - self._startTime
		return self._time

	@time.setter
	def time(self, value: float):
		self._time = value
