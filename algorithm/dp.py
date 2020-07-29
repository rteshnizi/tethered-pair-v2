import utils.cgal.geometry as Geom
from math import fabs, nan, isnan
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.node import Node
from algorithm.cable import tightenCable, getLongCable
from model.modelService import Model
from model.vertex import Vertex
from utils.priorityQ import PriorityQ
from utils.cgal.types import Polygon

model = Model()

def dynamicProg(debug=False) -> Node:
	distA = []
	cableA = []
	distB = []
	cableB = []
	numNodesOnCable = len(model.cable)
	solution: Node = None
	for i in range(numNodesOnCable):
		cableSection = model.cable[i:numNodesOnCable]
		solution = aStarSingle(cableSection, model.robots[0].destination, baseIndex=-1, robotIndex=0, debug=debug)
	return solution

def aStarSingle(cable, dest, baseIndex, robotIndex, debug=False) -> Node:
	"""
	baseIndex and robotIndex: 0 | -1
	"""
	nodeMap = {} # We keep a mpa of nodes here to update their child-parent relationship
	q = PriorityQ(key1=Node.pQGetPrimaryCost, key2=Node.pQGetSecondaryCost) # The Priority Queue container
	if debug: print("Initial Cable Length = ", Geom.lengthOfCurve(cable))
	root = Node(cable=cable, parent=None, fractions=[1, 1])
	q.enqueue(root)
	count = 0
	destinationsFound = 0
	while not q.isEmpty():
		n: Node = q.dequeue()
		count += 1
		if debug: print("-------------MAX=%.2f, MIN=%.2f @ %s-------------" % (Node.pQGetPrimaryCost(n), Node.pQGetSecondaryCost(n), getCableId(n.cable, n.fractions)))
		if isAtDestination(n):
			if debug: print("At Destination after visiting %d nodes, discovering %d configs" % (count, len(nodeMap)))
			destinationsFound += 1
			return n # For now terminate at first solution
		base = n.cable[baseIndex]
		gaps = n.cable[robotIndex].gaps if n.cable[robotIndex].name != dest.name else {n.cable[robotIndex]}
		for gap in gaps:
			if isUndoingLastMove(n, gap, robotIndex): continue
			if areBothStaying(n, base, gap): continue
			newCable = None
			# FIXME: Defensively ignoring exceptions
			try:
				newCable = tightenCable(n.cable, base, gap)
			except:
				continue
			l = Geom.lengthOfCurve(newCable)
			if l <= model.MAX_CABLE:
				addChildNode(newCable, n, nodeMap, q, debug)
	if debug: print("Total Nodes: %d, %d configs, %d destinations" % (count, len(nodeMap), destinationsFound))
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
		if debug: print("UPDATE %s @ %s" % (repr(nodeMap[cableStr].f), cableStr))
	else:
		child = Node(cable=newCable, parent=parent, fractions=fractions)
		if debug: print("ADDING %s @ %s" % (repr(child.f), cableStr))
		nodeMap[cableStr] = child
		pQ.enqueue(child)
