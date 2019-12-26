from algorithm.triangulation import Triangulation
from utils.cgal.types import Point
import utils.cgal.geometry as Geom
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual

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
				self._updateFunnelRight2(e[0])
				self._updateFunnelLeft2(e[1])
			else:
				self._updateFunnelLeft2(e[0])
				self._updateFunnelRight2(e[1])
			midPrev = mid

	def _addFirstTriangleToFunnel(self, mid, pt1, pt2):
		if Geom.isToTheRight(self.apex(), mid, pt1):
			self._funnelRight.append(convertToPoint(pt1))
			self._funnelLeft.append(convertToPoint(pt2))
		else:
			self._funnelLeft.append(convertToPoint(pt1))
			self._funnelRight.append(convertToPoint(pt2))

	def _updateFunnelLeft2(self, candidate) -> None:
		(self._funnelLeft, self._funnelRight) = self._updateFunnelSide(candidate, True)

	def _updateFunnelRight2(self, candidate):
		(self._funnelRight, self._funnelLeft) = self._updateFunnelSide(candidate, False)

	# TODO: Reuse _walkFunnelSide() for when we are past apex as well
	def _updateFunnelSide(self, candidate, isUpdatingLeft: bool):
		# The terminology in this function is weird because this function is agnostic to which side of the funnel it is updating
		candidate = convertToPoint(candidate)
		mySideOfFunnel = self._funnelLeft if isUpdatingLeft else self._funnelRight
		otherSideOfFunnel = self._funnelRight if isUpdatingLeft else self._funnelLeft
		# If the point is already on the funnel side then skip it
		if mySideOfFunnel[0] == candidate or mySideOfFunnel[-1] == candidate: return (mySideOfFunnel, otherSideOfFunnel)
		index = self._walkFunnelSide(candidate, mySideOfFunnel, isUpdatingLeft)
		if index > 0:
			mySideOfFunnel = mySideOfFunnel[:index]
			mySideOfFunnel.append(candidate)
			return (mySideOfFunnel, otherSideOfFunnel)
		# At this point we are starting to walk the other side of the funnel
		# check if the candidate should be placed at index 0
		isStrictlyOutsideFunnel = Geom.isToTheRight if isUpdatingLeft else Geom.isToTheLeft
		isStrictlyInsideFunnel = Geom.isToTheLeft if isUpdatingLeft else Geom.isToTheRight
		pt1 = self._others[-1]
		pt2 = otherSideOfFunnel[0]
		if isStrictlyInsideFunnel(pt1, pt2, candidate):
			return ([candidate], otherSideOfFunnel)
		# At this point we are past the apex, so the apex will have to be changed
		for i in range(len(otherSideOfFunnel) - 1):
			pt1 = otherSideOfFunnel[i]
			pt2 = otherSideOfFunnel[i + 1]
			if isStrictlyInsideFunnel(pt1, pt2, candidate):
				mySideOfFunnel = [candidate]
				self._others = self._others + otherSideOfFunnel[:i + 1]
				otherSideOfFunnel = otherSideOfFunnel[i + 1:]
				return (mySideOfFunnel, otherSideOfFunnel)
		mySideOfFunnel = [candidate]
		self._others = self._others + otherSideOfFunnel
		otherSideOfFunnel = [self._others[-1]]
		return (mySideOfFunnel, otherSideOfFunnel)

	def _walkFunnelSide(self, target, funnelSide: list, isCheckingLeft: bool) -> int:
		isStrictlyInsideFunnel = Geom.isToTheRight if isCheckingLeft else Geom.isToTheLeft
		isStrictlyOutsideFunnel = Geom.isToTheLeft if isCheckingLeft else Geom.isToTheRight
		# initial check: whether the candidate is beyond the funnel
		pt1 = self._others[-1]
		pt2 = funnelSide[-1]
		if len(funnelSide) > 1:
			pt1 = funnelSide[-2]
		if isStrictlyOutsideFunnel(pt1, pt2, target):
			return len(funnelSide)
		for i in reversed(range(1, len(funnelSide))):
			pt1 = funnelSide[i - 1]
			pt2 = funnelSide[i]
			(eq, dist) = almostEqual(pt2, target) # used to say pt2 == target
			if eq or isStrictlyInsideFunnel(pt1, pt2, target):
				return i
		return 0

	def _findCandidatePath(self, dest, funnelSide: list, isCheckingLeft: bool):
		index = self._walkFunnelSide(dest, funnelSide, isCheckingLeft)
		funnelSide = funnelSide[:index]
		return self._others + funnelSide + [convertToPoint(dest)]

	def getShortestPath(self, dest):
		# If sleeve is a single triangle, the path is from apex to destination
		if len(self.sleeve) == 1: return self._others + [convertToPoint(dest)]
		mid = Geom.midpoint(self._funnelLeft[0], self._funnelRight[0])
		shouldGoLeft = Geom.isToTheLeft(self.apex(), mid, dest)
		if shouldGoLeft: return self._findCandidatePath(dest, self._funnelLeft, True)
		return self._findCandidatePath(dest, self._funnelRight, False)
