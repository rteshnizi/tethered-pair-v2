from triangulation import Triangulation
from utils.cgal.types import Point
import utils.cgal.geometry as Geom
from collections import deque

class Funnel:
	def __init__(self, apex: Point, dest: Point, triangulation: Triangulation, sleeve: list):
		self.apex = apex
		self.dest = dest
		self.tri = triangulation
		self.sleeve = sleeve
		self._funnel = deque()
		self._addFirstTriangleToFunnel()
		self._build()

	def _addFirstTriangleToFunnel(self):
		e = self.tri.getCommonEdge(self.sleeve[i], self.sleeve[i + 1])
		if not e:
			raise RuntimeError("Sleeve must have neighboring triangles.")
		e = list(e)
		mid = Geom.midpoint(e[0], e[1])
		if Geom.isToTheRight(self.apex, mid, e[0]):
			self._funnel.append(e[0])
			self._funnel.appendleft(e[1])
		else:
			self._funnel.append(e[1])
			self._funnel.appendleft(e[0])

	def _build(self):
		pass
