import utils.cgal.geometry as Geom
from model.modelService import Model
from model.robot import Robot
from utils.cgal.types import Ray, Segment, convertToPoint, intersection

model = Model()

class LabeledVert(object):
	def __init__(self, vertex, robot):
		self.vrt = vertex
		self.rbt = robot

	def __repr__(self):
		return "<%s, %s>" % (self.vrt.name, self.rbt.name)

def findGaps(v, r: Robot):
	# TODO: Only look at gaps that are inside the bounding box (or partially inside)
	if v.loc == r.destination.loc:
		return [LabeledVert(r.destination, r)]
	verts = []
	if _isGap(v, r.destination):
		verts.append(LabeledVert(r.destination, r))
	for u in model.vertices:
		# This is for the edge case in which the destination is on the vertex exactly
		if u.loc == r.destination.loc: continue
		if _isGap(v, u):
			verts.append(LabeledVert(u, r))
	return verts

def _isGap(src, target) -> bool:
	if not src.isVisible(target):
		return False
	# Detecting whether u is a gap for v
	epsilon = Geom.getEpsilonVector(src, target)
	if target.ownerObs and target.ownerObs.enclosesPoint(target.loc + epsilon):
		return False
	return True


def applyMovement(cable, dest, isZeroEndMoving: bool):
	cable = doPops(cable, dest, isZeroEndMoving)
	cable = doPushes(cable, dest, isZeroEndMoving)
	return cable

def doPops(cable, dest, isZeroEndMoving):
	src = cable[0] if isZeroEndMoving else cable[-1]
	movement = Segment(convertToPoint(src), convertToPoint(dest))
	stitches = getPoppingStitchLines(cable, isZeroEndMoving)
	deleteInd = 1 if isZeroEndMoving else -2
	for stitch in stitches:
		inter = intersection(movement, stitch)
		if inter:
			del cable[deleteInd]
		else:
			break
	return cable

def doPushes(cable, dest, isZeroEndMoving):
	src = cable[-1] if isZeroEndMoving else cable[0]
	movement = Segment(convertToPoint(src), convertToPoint(dest))
	base = cable[0] if isZeroEndMoving else cable[-1]
	closestBase = None
	closestDist = 1000000000
	for v in model.vertices:
		if _isGap(base, v):
			basePt = convertToPoint(base)
			vPt = convertToPoint(v)
			stitch = Ray(vPt, v - basePt)
			inter = intersection(movement, stitch)
			if inter:
				d = Geom.vertexDistance(src, inter)
				if d < closestDist:
					closestDist = d
					closestBase = v
	insertionIndex = -1 if isZeroEndMoving else 1
	while closestDist:
		cable.insert(insertionIndex, closestBase)
		#  Continue Here

def getPoppingStitchLines(cable: list, isZeroEndMoving: bool) -> list:
	rays = []
	start = len(cable) - 1 if isZeroEndMoving else 0
	stop = 1 if isZeroEndMoving else len(cable) - 2
	step = -1 if isZeroEndMoving else 1
	for i in range(start, stop, step):
		pt1 = convertToPoint(cable[i])
		pt2 = convertToPoint(cable[i + step])
		direction = pt2 - pt1
		r = Ray(pt2, direction)
		rays.append(r)
	rays.reverse()
	return rays
