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

def aStar(debug=False) -> Node:
	# visited = set()
	nodeMap = {} # We keep a mpa of nodes here to update their child-parent relationship
	q = PriorityQ(key1=Node.pQGetPrimaryCost, key2=Node.pQGetSecondaryCost) # The Priority Queue container
	if debug: print("Initial Cable Length = ", Geom.lengthOfCurve(model.cable))
	root = Node(cable=model.cable, parent=None)
	q.enqueue(root)
	parent: Node = None
	count = 0
	while not q.isEmpty():
		n: Node = q.dequeue()
		count += 1
		# visited.add(n)
		if debug: print("-------------MAX=%.2f, MIN=%.2f @ %s-------------" % (Node.pQGetPrimaryCost(n), Node.pQGetSecondaryCost(n), getCableId(n.cable)))
		if isAtDestination(n):
			if debug: print("At Destination after visiting %d nodes" % count)
			return n # For now terminate at first solution
		for va in n.cable[0].gaps:
			if isUndoingLastMove(n, va, 0): continue
			for vb in n.cable[-1].gaps:
				if isUndoingLastMove(n, vb, -1): continue
				if areBothStaying(n, va, vb): continue
				# For now I deliberately avoid cross movement because it crashes the triangulation
				# In reality we can fix this by mirorring the space (like I did in the previous paper)
				if isThereCrossMovement(n.cable, va, vb): continue
				newCable = tightenCable(n.cable, va, vb)
				l = Geom.lengthOfCurve(newCable)
				if l <= model.MAX_CABLE:
					addChildNode(newCable, n, nodeMap, q, debug)
				# else:
				# 	frac = getPartialMotion(n.cable, newCable, True)
				# 	if isnan(frac): pass
				# 	p2 = getPartialMotion(n.cable, newCable, False)
				# 	reza = 0
	return None

def isUndoingLastMove(node, v, index):
	if not node.parent: return False
	if convertToPoint(node.parent.cable[index]) != convertToPoint(v): return False
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

def getCableId(cable, fractions=[1, 1]) -> str:
	return "%s-[%.6f, %.6f]" % (repr(cable), fractions[0], fractions[0])

def addChildNode(newCable, parent, nodeMap, pQ, debug, fractions=[1, 1]) -> None:
	cableStr = getCableId(newCable)
	if cableStr in nodeMap:
		nodeMap[cableStr].updateParent(parent)
		if debug: print("UPDATE %s @ %s" % (repr(nodeMap[cableStr].f), cableStr))
	else:
		child = Node(cable=newCable, parent=parent)
		if debug: print("ADDING %s @ %s" % (repr(child.f), cableStr))
		nodeMap[cableStr] = child
		pQ.enqueue(child)

def getPartialMotion(oldCable, newCable, isRobotA) -> float:
	me = 0 if isRobotA else -1
	other = -1 if isRobotA else 0
	src = oldCable[me]
	dst = newCable[me]
	start = 0
	end = 1
	maxFrac = nan
	maxVert = None
	# Binary search for an approximation of the fraction
	while fabs(start - end) > 1e-5:
		frac = (start + end) / 2
		newDst = Geom.getPointOnLineSegment(src, dst, frac)
		v = Vertex(name="", loc=newDst, ownerObs=None)
		model.addTempVertex(v, isRobotA)
		tight = tightenCable(oldCable, v, newCable[other]) if isRobotA else tightenCable(oldCable, newCable[other], v)
		l = Geom.lengthOfCurve(tight)
		if l <= model.MAX_CABLE:
			maxFrac = frac
			maxVert = v
			start = (start + end) / 2
		else:
			end = (start + end) / 2
		model.removeEntity(v)
	# Save this vertex for future searches
	if maxVert: model.addTempVertex(maxVert, isRobotA)
	return maxFrac
