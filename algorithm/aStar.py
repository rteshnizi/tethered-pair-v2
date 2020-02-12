import utils.cgal.geometry as Geom
from math import fabs, nan
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.node import Node
from algorithm.cable import tightenCable, getLongCable, findSegments
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
		if debug: print("-------------%s @ MAX=%.2f, MIN=%.2f-------------" % (repr(n.cable), Node.pQGetPrimaryCost(n), Node.pQGetSecondaryCost(n)))
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
					cableStr = repr(newCable)
					if cableStr in nodeMap:
						nodeMap[cableStr].updateParent(n)
					else:
						child = Node(cable=newCable, parent=n)
						# if child in visited: continue
						if debug:
							verts = ("%s-%s" % (va.name, vb.name)).ljust(9)
							print("ADDING %s @ %s" % (verts, repr(child.f)))
						nodeMap[cableStr] = child
						q.enqueue(child)
				else:
					p1 = getPartialMotion(n.cable, newCable, True)
					p1 = getPartialMotion(n.cable, newCable, False)
					reza = 0
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

def getPartialMotion(oldCable, newCable, isRobotA) -> float:
	ind = 0 if isRobotA else -1
	other = -1 if isRobotA else 0
	src = oldCable[ind]
	dst = newCable[ind]
	n = len(newCable)
	start = 0
	end = 1
	while fabs(start - end) > 1e-5:
		frac = (start + end) / 2
		newDst = Geom.getPointOnLineSegment(src, dst, frac)
		v = Vertex(name="tmp-a", loc=newDst, ownerObs=None)
		model.addTempVertex(v, isRobotA)
		tight = tightenCable(oldCable, v, newCable[other])
		l = Geom.lengthOfCurve(tight)
		if l <= model.MAX_CABLE:
			print("YAY")
		else:
			print("NAY")
		model.removeEntity(v)
		ttt = 0
	if n == 2:
		pt = newCable[0]
		h = Geom.pointAndLineDistance(pt, src, dst)
		traveledDist = Geom.reversePythagorean(model.MAX_CABLE, h)
		rrrr = Geom.reza(src, dst, pt, traveledDist)
		yolo = 0
	for i in reversed(range(1, n - 1)):
		v1 = newCable[i - 1]
		v2 = newCable[i]
		Geom.getLineSegAndRayIntersection(src, dst, v1, v2)
