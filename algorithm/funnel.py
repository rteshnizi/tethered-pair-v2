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
		self._build()

	def _build(self):
		ePrev = self.tri.getCommonEdge(self.sleeve[0], self.sleeve[1])
		# So we can access with index
		ePrev = list(ePrev)
		midPrev = Geom.midpoint(ePrev[0], ePrev[1])
		self._addFirstTriangleToFunnel(midPrev, ePrev[0], ePrev[1])
		for i in range(1, len(self.sleeve) - 1):
			e = self.tri.getCommonEdge(self.sleeve[i], self.sleeve[i + 1])
			e = list(e)
			mid = Geom.midpoint(e[0], e[1])
			if Geom.isToTheRight(midPrev, mid, e[0]):
				self._updateFunnelRight(e[0])
				self._updateFunnelLeft(e[1])
			else:
				self._updateFunnelLeft(e[0])
				self._updateFunnelRight(e[1])

	def _addFirstTriangleToFunnel(self, mid, pt1, pt2):
		if Geom.isToTheRight(self.apex, mid, pt1):
			self._funnelRight.append(convertToPoint(pt1))
			self._funnelLeft.append(convertToPoint(pt2))
		else:
			self._funnelLeft.append(convertToPoint([1]))
			self._funnelRight.append(convertToPoint([0]))

	def _updateFunnelLeft(self, candidate):
		pt = convertToPoint(candidate)
		if self._funnel[0] == pt or self._funnel[-1] == pt: return
		Geom.intersectSegmentAndSegment
		for i in range(len(self._funnel) - 1):
			pass

	def _updateFunnelRight(self, candidate):
		pass
