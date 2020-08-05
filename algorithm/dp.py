import utils.cgal.geometry as Geom
from math import fabs, nan, isnan, inf
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered, findSubCable
from algorithm.node import Node, Cost
from algorithm.cable import tightenCable, getLongCable
from algorithm.solutionLog import SolutionLog, Solution
from model.modelService import Model
from model.vertex import Vertex
from utils.priorityQ import PriorityQ
from utils.cgal.types import Polygon
from utils.logger import Logger

model = Model()
logger = Logger()

def dynamicProg(debug=False) -> list:
	logger.log("##############################################")
	logger.log("##################  D----P  ##################")
	logger.log("CABLE-O: %s - L = %.2f" % (repr(model.cable), Geom.lengthOfCurve(model.cable)))
	distA = []
	cableA = []
	pathA = []
	distB = []
	cableB = []
	pathB = []
	solution = SolutionLog(model.MAX_CABLE)
	runningSolution: SolutionLog = None
	for i in range(len(model.cable)):
		indices = [0, -1]
		for robotIndex in indices:
			cableSection = model.cable[i:] if robotIndex == 0 else model.cable[:i + 1]
			baseIndex = -1 if robotIndex == 0 else 0
			distArr = distA if robotIndex == 0 else distB
			cableArr = cableA if robotIndex == 0 else cableB
			pathArr = pathA if robotIndex == 0 else pathB
			runningSolution = aStarSingle(model.cable, model.robots[robotIndex].destination, baseIndex=baseIndex, robotIndex=robotIndex, enforceCable=cableSection, debug=debug)
			solution.expanded += runningSolution.expanded
			solution.genereted += runningSolution.genereted
			if runningSolution.content:
				ind = findSubCable(runningSolution.content.cable, cableSection[1:] if robotIndex == 0 else cableSection[:-1])
				if ind < 0:
					raise RuntimeError("What?")
				dist = runningSolution.content.cost[robotIndex] + Geom.lengthOfCurve(model.cable[:i + 1] if robotIndex == 0 else model.cable[i:])
				subCable = runningSolution.content.cable[:ind] if robotIndex == 0 else runningSolution.content.cable[ind + len(cableSection) - 1:]
				path = runningSolution.content.paths[robotIndex]
			else:
				dist = inf
				subCable = None
				path = None
			distArr.append(dist)
			cableArr.append(subCable)
			pathArr.append(path)

	minCost = Cost()
	paths = [None, None]
	solutionCable = None
	for i in range(len(model.cable)):
		if not cableA[i]: continue
		for j in range(i, len(model.cable)):
			if not cableB[j]: continue
			c = cableA[i] + model.cable[i + 1:j] + cableB[j]
			if Geom.lengthOfCurve(c) > model.MAX_CABLE: continue
			d = Cost([distA[i], distB[j]])
			if d.max()[0] < minCost.max()[0] or (d.max()[0] == minCost.max()[0] and d.min()[0] < minCost.min()[0]):
				minCost = d
				paths = [pathA[i], pathB[j]]
				solutionCable = c
	solution.content = Solution(solutionCable, paths, minCost)
	logger.log("At Destination after expanded %d nodes, discovering %d configs" % (solution.expanded, solution.genereted))
	return solution

def aStarSingle(cable, dest, baseIndex, robotIndex, enforceCable=None, debug=False) -> SolutionLog:
	"""
	baseIndex and robotIndex: 0 | -1
	"""
	solutionLog = SolutionLog()
	nodeMap = {} # We keep a map of nodes here to update their child-parent relationship
	q = PriorityQ(key1=Node.pQGetPrimaryCost, key2=Node.pQGetSecondaryCost) # The Priority Queue container
	if debug: logger.log("CABLE-O: %s - L = %.2f" % (repr(cable), Geom.lengthOfCurve(cable)))
	root = Node(cable=cable, parent=None, fractions=[1, 1])
	q.enqueue(root)
	count = 0
	destinationsFound = 0
	while not q.isEmpty():
		n: Node = q.dequeue()
		count += 1
		if debug: logger.log("-------------MAX=%.2f, MIN=%.2f @ %s-------------" % (Node.pQGetPrimaryCost(n), Node.pQGetSecondaryCost(n), getCableId(n.cable, n.fractions)))
		if isAtDestination(n, dest, robotIndex):
			solutionLog.content = Solution.createFromNode(n)
			solutionLog.expanded = count
			solutionLog.genereted = len(nodeMap)
			if debug: logger.log("At Destination after expanded %d nodes, discovering %d configs" % (solutionLog.expanded, solutionLog.genereted))
			destinationsFound += 1
			return solutionLog
		base = n.cable[baseIndex]
		gaps = n.cable[robotIndex].gaps if n.cable[robotIndex].name != dest.name else {n.cable[robotIndex]}
		for gap in gaps:
			if gap.name == n.cable[baseIndex].name: continue
			if isUndoingLastMove(n, gap, robotIndex): continue
			if areBothStaying(n, gap if robotIndex == 0 else base, base if robotIndex == 0 else gap): continue
			newCable = None
			# FIXME: Defensively ignoring exceptions
			try:
				newCable = tightenCable(n.cable, gap if robotIndex == 0 else base, base if robotIndex == 0 else gap)
			except Exception as err:
				model.removeTriangulationEdges()
				continue
			if enforceCable:
				ind = findSubCable(newCable, enforceCable[1:] if robotIndex == 0 else enforceCable[:-1])
				if ind < 0: continue
			l = Geom.lengthOfCurve(newCable)
			if l <= model.MAX_CABLE:
				addChildNode(newCable, n, nodeMap, q, debug)
	if debug: logger.log("Total Nodes: %d, %d configs, %d destinations" % (count, len(nodeMap), destinationsFound))
	solutionLog.expanded = count
	solutionLog.genereted = len(nodeMap)
	solutionLog.setEndTime()
	return solutionLog

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

def isAtDestination(n, dest, robotIndex) -> bool:
	if not n: return False

	return convertToPoint(n.cable[robotIndex]) == convertToPoint(dest)

def getCableId(cable, fractions) -> str:
	# return "%s-[%.6f, %.6f]" % (repr(cable), fractions[0], fractions[1])
	return repr(cable)

def addChildNode(newCable, parent, nodeMap, pQ, debug, fractions=[1, 1]) -> None:
	cableStr = getCableId(newCable, fractions)
	if cableStr in nodeMap:
		nodeMap[cableStr].updateParent(parent)
		if debug: logger.log("UPDATE %s @ %s" % (repr(nodeMap[cableStr].f), cableStr))
	else:
		child = Node(cable=newCable, parent=parent, fractions=fractions)
		if debug: logger.log("ADDING %s @ %s" % (repr(child.f), cableStr))
		nodeMap[cableStr] = child
		pQ.enqueue(child)
