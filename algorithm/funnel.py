from algorithm.triangulation import Triangulation
from utils.cgal.types import Point
import utils.cgal.geometry as Geom
from utils.vertexUtils import convertToPoint, getClosestVertex
from collections import deque

class Funnel:
	def __init__(self, src: Point, triangulation: Triangulation, sleeve: list):
		self.tri = triangulation
		self.src = self.tri.pushVertEpsilonInside(src, sleeve[0])
		self.sleeve = sleeve
		self._funnelLeft = []
		self._funnelRight = []
		self._others = [self.src]
		self._build()
		self._others[0] = convertToPoint(src)

	def apex(self):
		return self._others[-1]

	def _build(self):
		if len(self.sleeve) == 1: return
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
			midPrev = mid

	def _addFirstTriangleToFunnel(self, mid, pt1, pt2):
		if Geom.isToTheRight(self.apex(), mid, pt1):
			self._funnelRight.append(convertToPoint(pt1))
			self._funnelLeft.append(convertToPoint(pt2))
		else:
			self._funnelLeft.append(convertToPoint(pt1))
			self._funnelRight.append(convertToPoint(pt2))

	# TODO: Use self._walkFunnelSide
	def _updateFunnelLeft(self, candidate):
		candidate = convertToPoint(candidate)
		if self._funnelLeft[0] == candidate or self._funnelLeft[-1] == candidate: return
		# initial check
		pt1 = self._others[-1]
		pt2 = self._funnelLeft[-1]
		if len(self._funnelLeft) > 1:
			pt1 = self._funnelLeft[-2]
		if Geom.isToTheLeft(pt1, pt2, candidate):
			self._funnelLeft.append(candidate)
			return
		for i in reversed(range(len(self._funnelLeft) - 1)):
			if i == 0: break
			pt1 = self._funnelLeft[i - 1]
			pt2 = self._funnelLeft[i]
			if Geom.isToTheRight(pt1, pt2, candidate):
				self._funnelLeft = self._funnelLeft[:i]
				self._funnelLeft.append(candidate)
				return
		pt1 = self._others[-1]
		pt2 = self._funnelRight[0]
		if Geom.isToTheLeft(pt1, pt2, candidate):
			self._funnelLeft = [candidate]
			return
		# At this point we are past the apex, so the apex will have to be changed
		for i in range(len(self._funnelRight) - 1):
			pt1 = self._funnelRight[i]
			pt2 = self._funnelRight[i + 1]
			if Geom.isToTheLeft(pt1, pt2, candidate):
				self._funnelLeft = [candidate]
				self._others = self._others + self._funnelRight[:i + 1]
				self._funnelRight = self._funnelRight[i + 1:]
				return
		self._funnelLeft = [candidate]
		self._others = self._others + self._funnelRight
		self._funnelRight = [self._others[-1]]

	# TODO: Use self._walkFunnelSide
	def _updateFunnelRight(self, candidate):
		candidate = convertToPoint(candidate)
		if self._funnelRight[0] == candidate or self._funnelRight[-1] == candidate: return
		# initial check
		pt1 = self._others[-1]
		pt2 = self._funnelRight[-1]
		if len(self._funnelRight) > 1:
			pt1 = self._funnelRight[-2]
		if Geom.isToTheRight(pt1, pt2, candidate):
			self._funnelRight.append(candidate)
			return
		for i in reversed(range(len(self._funnelRight) - 1)):
			if i == 0: break
			pt1 = self._funnelRight[i - 1]
			pt2 = self._funnelRight[i]
			if Geom.isToTheLeft(pt1, pt2, candidate):
				self._funnelRight = self._funnelRight[:i]
				self._funnelRight.append(candidate)
				return
		pt1 = self._others[-1]
		pt2 = self._funnelLeft[0]
		if Geom.isToTheRight(pt1, pt2, candidate):
			self._funnelRight = [candidate]
			return
		# At this point we are past the apex, so the apex will have to be changed
		for i in range(len(self._funnelLeft) - 1):
			pt1 = self._funnelLeft[i]
			pt2 = self._funnelLeft[i + 1]
			if Geom.isToTheRight(pt1, pt2, candidate):
				self._funnelRight = [candidate]
				self._others = self._others + self._funnelLeft[:i + 1]
				self._funnelLeft = self._funnelLeft[i + 1:]
				return
		self._funnelRight = [candidate]
		self._others = self._others + self._funnelLeft
		self._funnelLeft = [self._others[-1]]

	def _walkFunnelSide(self, target, funnelSide: list, isCheckingLeft: bool) -> int:
		isInsideFunnel = Geom.isToTheRight if isCheckingLeft else Geom.isToTheLeft
		isOutsideFunnel = Geom.isToTheLeft if isCheckingLeft else Geom.isToTheRight
		# initial check
		pt1 = self._others[-1]
		pt2 = funnelSide[-1]
		if len(funnelSide) > 1:
			pt1 = funnelSide[-2]
		if isOutsideFunnel(pt1, pt2, target):
			return len(funnelSide)
		for i in reversed(range(len(funnelSide) - 1)):
			if i == 0: break
			pt1 = funnelSide[i - 1]
			pt2 = funnelSide[i]
			if isInsideFunnel(pt1, pt2, candidate):
				return i
		return 0

	def _findCandidatePath(self, dest, funnelSide: list, isCheckingLeft: bool):
		index = self._walkFunnelSide(dest, funnelSide, isCheckingLeft)
		funnelSide = funnelSide[:index]
		return self._others + funnelSide + [convertToPoint(dest)]

	def getShortestPath(self, dest):
		mid = Geom.midpoint(self._funnelLeft[0], self._funnelRight[0])
		shouldGoLeft = Geom.isToTheLeft(self.apex(), mid, dest)
		if shouldGoLeft: return self._findCandidatePath(dest, self._funnelLeft, True)
		return self._findCandidatePath(dest, self._funnelRight, False)
