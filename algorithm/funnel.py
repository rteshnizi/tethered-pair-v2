from algorithm.triangulation import Triangulation
from utils.cgal.types import Point, convertToPoint
import utils.cgal.geometry as Geom
from collections import deque

class Funnel:
	def __init__(self, src: Point, dest: Point, triangulation: Triangulation, sleeve: list):
		self.src = src
		self.dest = dest
		self.tri = triangulation
		self.sleeve = sleeve
		self._funnelLeft = []
		self._funnelRight = []
		self._others = []
		self.apex = src
		self._addFirstTriangleToFunnel()
		if len(sleeve) == 1: return
		self._build()

	def _addFirstTriangleToFunnel(self):
		e = self.tri.getCommonEdge(self.sleeve[0], self.sleeve[1])
		if not e:
			raise RuntimeError("Sleeve must have neighboring triangles.")
		e = list(e)
		mid = Geom.midpoint(e[0], e[1])
		if Geom.isToTheRight(self.apex, mid, e[0]):
			self._funnelRight.append(convertToPoint(e[0]))
			self._funnelLeft.append(convertToPoint([1]))
		else:
			self._funnelLeft.append(convertToPoint([1]))
			self._funnelRight.append(convertToPoint([0]))

	def _build(self):
		for i in range(1, len(self.sleeve) - 1):
			e = self.tri.getCommonEdge(self.sleeve[i], self.sleeve[i + 1])
			# So we can access with index
			e = list(e)
			if Geom.isToTheRight(self.apex, mid, e[0]):
				self._updateFunnelRight(e[0])
				self._updateFunnelLeft(e[1])
			else:
				self._updateFunnelLeft(e[0])
				self._updateFunnelRight(e[1])

	def _updateFunnelLeft(self, candidate):
		pt = convertToPoint(candidate)
		if self._funnel[0] == pt or self._funnel[-1] == pt: return
		Geom.intersectSegmentAndSegment
		for i in range(len(self._funnel) - 1):
			pass

	def _updateFunnelRight(self, candidate):
		pass
