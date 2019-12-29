import utils.cgal.geometry as Geom
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.node import Node
from algorithm.cable import tightenCable, getLongCable
from model.modelService import Model
from utils.priorityQ import PriorityQ
from utils.cgal.types import Polygon

model = Model()

def aStar(debug=False) -> Node:
	# visited = set()
	q = PriorityQ(key1=Node.pQGetPrimaryCost, key2=Node.pQGetSecondaryCost) # The Priority Queue container
	if debug: print("Initial Cable Length = ", Geom.lengthOfCurve(model.cable))
	root = Node(cable=model.cable, parent=None)
	q.enqueue(root)
	while not q.isEmpty():
		n: Node = q.dequeue()
		# visited.add(n)
		if isAtDestination(n):
			if debug: print("At Destination")
			return n # For now terminate at first solution
		if debug: print("-------------NEW NODE-------------", n)
		for va in n.cable[0].gaps:
			for vb in n.cable[-1].gaps:
				# For now I deliberately avoid cross movement because it crashes the triangulation
				# In reality we can fix this by mirorring the space (like I did in the previous paper)
				if areBothStaying(n, va, vb): continue
				if isThereCrossMovement(n.cable, va, vb): continue
				newCable = tightenCable(n.cable, va, vb)
				l = Geom.lengthOfCurve(newCable)
				if l <= model.MAX_CABLE:
					child = Node(cable=newCable, parent=n)
					# if child in visited: continue
					if debug:
						verts = ("%s-%s" % (va.name, vb.name)).ljust(9)
						print("ADDING %s @ %s" % (verts, repr(child.g)))
					n.children.append(child)
					q.enqueue(child)
	return None

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
	return convertToPoint(n.cable[0]) == convertToPoint(model.robots[0].destination) and convertToPoint(n.cable[-1]) == convertToPoint(model.robots[1].destination)
