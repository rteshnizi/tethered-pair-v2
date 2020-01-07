import utils.cgal.geometry as Geom
from model.modelService import Model
from model.debugEdge import DebugEdge
from model.robot import Robot
from utils.cgal.types import Ray, Segment, intersection
from utils.vertexUtils import convertToPoint


model = Model()

class LabeledVert(object):
	def __init__(self, vertex, robot):
		self.vrt = vertex
		self.rbt = robot

	def __repr__(self):
		return "<%s, %s>" % (self.vrt.name, self.rbt.name)

def processReducedVisibilityGraph(debug=False) -> None:
	"""
	Note that reduced visibility graph is unidirectional. That is, there might be and edge v -> u but not the other way around
	"""
	for v in model.allVertexObjects:
		for u in model.allVertexObjects:
			if v.name == u.name and (v.name == "D1" or v.name == "D2"):
				v.gaps.add(u)
				continue
			if v.loc == u.loc:
				# v.gaps.add(u)
				continue
			# The below 2 edge cases rarely happen, but it happens when the robot or destination are exactly at a vertex of an obstacle
			if _isRobotOrDestinationAndOnObstacleButNotAdjacent(v, u): continue
			if _isRobotOrDestinationAndOnObstacleButNotAdjacent(u, v): continue

			# If they belong to the same obstacle but are not adjacent, they aren't u is not visible
			if v.ownerObs and u.ownerObs and v.ownerObs.name == u.ownerObs.name and u not in v.adjacentOnObstacle: continue
			if _isGap(v, u):
				v.gaps.add(u)

	if not debug: return
	counter = 0
	for v in model.allVertexObjects:
		for u in v.gaps:
			e = DebugEdge("%s=>%s" % (v.name, u.name), [convertToPoint(v), convertToPoint(u)], isDirected=True)
			model.entities[e.name] = e
			e.createShape(model.canvas)
			counter += 1
	print("Edges: %d" % counter)

def _isRobotOrDestinationAndOnObstacleButNotAdjacent(candidate, obstacleVert):
	# FIXME: This is buggy:
	# What if candidate is a robot but obstacleVert is also a robot that happens to be on the same obstacle but are not adjacent
	# In that case we have to first find the relevant obstacle that both of the robots/destinations are on and perform this same function

	# candidate is not a robot or destination
	if candidate.ownerObs: return False
	# obstacleVert is a robot or destination
	if not obstacleVert.ownerObs: return False
	# The robot or destination is on the given obstacle
	if not obstacleVert.ownerObs.getVertex(candidate): return False
	# The robot or destination are on the given obstacle but is adjacent to the vertex of interest
	if obstacleVert.ownerObs.areAdjacent(candidate, obstacleVert): return False
	return True

def _isGap(src, target) -> bool:
	if not src.isVisible(target):
		return False
	# Detecting whether u is a gap for v
	epsilon = Geom.getEpsilonVector(src, target)
	if target.ownerObs and target.ownerObs.enclosesPoint(target.loc + epsilon):
		return False
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
	src = cable[0] if isZeroEndMoving else cable[-1]
	movement = Segment(convertToPoint(src), convertToPoint(dest))
	base = cable[1] if isZeroEndMoving else cable[-2]
	closestBase = None
	closestDist = 1000000000
	for v in model.vertices:
		if v.loc == base.loc: continue
		if _isGap(base, v):
			basePt = convertToPoint(base)
			vPt = convertToPoint(v)
			stitch = Ray(vPt, vPt - basePt)
			inter = intersection(movement, stitch)
			if inter:
				d = Geom.vertexDistance(src, inter)
				if d < closestDist:
					closestDist = d
					closestBase = v
	insertionIndex = -1 if isZeroEndMoving else 1
	if closestDist:
		cable.insert(insertionIndex, closestBase)
		return doPushes(cable, dest, isZeroEndMoving)
	else:
		return cable

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
