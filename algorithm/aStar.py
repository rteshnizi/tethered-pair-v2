import utils.cgal.geometry as Geom
from math import fabs, nan, isnan
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.node import Node
from algorithm.cable import tightenCable, getLongCable
from model.modelService import Model
from model.vertex import Vertex
from utils.priorityQ import PriorityQ
from utils.cgal.types import Polygon
from utils.logger import Logger
from algorithm.solutionLog import Solution, SolutionLog

model = Model()
logger = Logger()

def aStar(debug=False) -> SolutionLog:
	solutionLog = SolutionLog(model.MAX_CABLE)
	nodeMap = {} # We keep a map of nodes here to update their child-parent relationship
	q = PriorityQ(key1=Node.pQGetPrimaryCost, key2=Node.pQGetSecondaryCost) # The Priority Queue container
	logger.log("##############################################")
	logger.log("##################  A-STAR  ##################")
	logger.log("CABLE-O: %s - L = %.2f" % (repr(model.cable), Geom.lengthOfCurve(model.cable)))
	root = Node(cable=model.cable, parent=None, debug=debug)
	q.enqueue(root)
	count = 0
	destinationsFound = 0
	while not q.isEmpty():
		n: Node = q.dequeue()
		count += 1
		# visited.add(n)
		if debug: logger.log("-------------MAX=%.2f, MIN=%.2f @ %s-------------" % (Node.pQGetPrimaryCost(n), Node.pQGetSecondaryCost(n), getCableId(n.cable, n.fractions)))
		if isAtDestination(n):
			solutionLog.content = Solution.createFromNode(n)
			solutionLog.expanded = count
			solutionLog.genereted = len(nodeMap)
			logger.log("At Destination after expanded %d nodes, discovering %d configs" % (solutionLog.expanded, solutionLog.genereted))
			destinationsFound += 1
			return solutionLog
		# Va = n.cable[0].gaps if n.fractions[0] == 1 else {n.cable[0]}
		Va = n.cable[0].gaps if n.cable[0].name != "D1" else {n.cable[0]}
		for va in Va:
			if isUndoingLastMove(n, va, 0): continue
			# Vb = n.cable[-1].gaps if n.fractions[1] == 1 else {n.cable[-1]}
			Vb = n.cable[-1].gaps if n.cable[-1].name != "D2" else {n.cable[-1]}
			for vb in Vb:
				if isUndoingLastMove(n, vb, -1): continue
				if areBothStaying(n, va, vb): continue
				# For now I deliberately avoid cross movement because it crashes the triangulation
				# In reality we can fix this by mirorring the space (like I did in the previous paper)
				if isThereCrossMovement(n.cable, va, vb): continue
				newCable = None
				# FIXME: Defensively ignoring exceptions
				try:
					newCable = tightenCable(n.cable, va, vb)
				except:
					continue
				l = Geom.lengthOfCurve(newCable)
				if l <= model.MAX_CABLE:
					addChildNode(newCable, n, nodeMap, q, debug)
				# else:
				# 	(frac, fracCable) = getPartialMotion(n.cable, newCable, isRobotA=True, debug=debug)
				# 	if not isnan(frac): addChildNode(fracCable, n, nodeMap, q, debug, fractions=[frac, 1])
				# 	(frac, fracCable) = getPartialMotion(n.cable, newCable, isRobotA=False, debug=debug)
				# 	if not isnan(frac): addChildNode(fracCable, n, nodeMap, q, debug, fractions=[1, frac])
	logger.log("Total Nodes: %d, %d configs, %d destinations" % (count, len(nodeMap), destinationsFound))
	return None

def isUndoingLastMove(node, v, index):
	if not node.parent: return False
	if v.name == "D1" or v.name == "D2": return False
	if convertToPoint(node.parent.cable[index]) != convertToPoint(v): return False
	path = node._getPath(index  == 0)
	path = removeRepeatedVertsOrdered(path)
	if convertToPoint(node.parent.cable[-2]) != convertToPoint(v): return False
	return True

def areBothStaying(parent, va, vb):
	if convertToPoint(parent.cable[0]) != convertToPoint(va): return False
	if convertToPoint(parent.cable[-1]) != convertToPoint(vb): return False
	return True

def isThereCrossMovement(cable, dest1, dest2):
	# I've also included the case where the polygon is not simple
	cable = getLongCable(cable, dest1, dest2)
	cable = removeRepeatedVertsOrdered(cable)
	if len(cable) < 3: return False
	p = Polygon([convertToPoint(v) for v in cable])
	return not p.is_simple()

def isAtDestination(n) -> bool:
	if not n: return False
	return convertToPoint(n.cable[0]) == convertToPoint(model.robots[0].destination) and convertToPoint(n.cable[-1]) == convertToPoint(model.robots[1].destination)

def getCableId(cable, fractions) -> str:
	# return "%s-[%.6f, %.6f]" % (repr(cable), fractions[0], fractions[1])
	return repr(cable)

def addChildNode(newCable, parent, nodeMap, pQ, debug, fractions=[1, 1]) -> None:
	cableStr = getCableId(newCable, fractions)
	if cableStr in nodeMap:
		nodeMap[cableStr].updateParent(parent)
		if debug: logger.log("UPDATE %s @ %s" % (repr(nodeMap[cableStr].f), cableStr))
	else:
		child = Node(cable=newCable, parent=parent, debug=debug, fractions=fractions)
		if debug: logger.log("ADDING %s @ %s" % (repr(child.f), cableStr))
		nodeMap[cableStr] = child
		pQ.enqueue(child)

def getPartialMotion(oldCable, newCable, isRobotA, debug) -> list:
	me = 0 if isRobotA else -1
	other = -1 if isRobotA else 0
	src = oldCable[me]
	dst = newCable[me]
	start = 0
	end = 1
	maxFrac = nan
	maxFracCable = None
	maxVert = None
	lastDistance = nan
	searchThreshold = 1e-2
	distanceThreshold = 1
	# Binary search for an approximation of the fraction
	while (isnan(lastDistance) or lastDistance > distanceThreshold) and fabs(start - end) > searchThreshold:
		frac = (start + end) / 2
		newDst = Geom.getPointOnLineSegment(src, dst, frac)
		if debug:
			inObstacle = False
			for o in model.obstacles:
				if o.enclosesPoint(newDst):
					inObstacle = True
					break
			if inObstacle:
				raise RuntimeError("WHUT?")
		v = model.getVertexByLocation(newDst.x(), newDst.y())
		# if not v: v = getClosestVertex(newDst)
		if not v: v = Vertex(name="tmp-vert", loc=newDst, ownerObs=None)
		model.addTempVertex(v, isRobotA)
		tight = tightenCable(oldCable, v, newCable[other]) if isRobotA else tightenCable(oldCable, newCable[other], v)
		l = Geom.lengthOfCurve(tight)
		if l <= model.MAX_CABLE:
			maxFrac = frac
			maxFracCable = tight
			lastDistance = Geom.vertexDistance(v, maxVert if maxVert else dst)
			maxVert = v
			start = (start + end) / 2
		else:
			end = (start + end) / 2
		model.removeTempVertex(v)
	# Save this vertex for future searches
	if maxVert:
		model.addTempVertex(maxVert, isRobotA)
		maxVert.gaps.add(dst)
	return (maxFrac, maxFracCable)
