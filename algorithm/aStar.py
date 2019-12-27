import utils.cgal.geometry as Geom
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.node import Node
from algorithm.cable import tightenCable, getLongCable
from model.modelService import Model
from utils.priorityQ import PriorityQ
from utils.cgal.types import Polygon

model = Model()

def aStar() -> Node:
	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	while not q.isEmpty():
		n: Node = q.dequeue()
		if isAtDestination(n):
			print("At Destination")
			return n # For now terminate at first solution
		print(n)
		for va in n.cable[0].gaps:
			for vb in n.cable[-1].gaps:
				print("%s-%s" % (va.name, vb.name))
				# For now I deliberately avoid cross movement because it crashes the triangulation
				# In reality we can fix this by mirorring the space (like I did in the previous paper)
				if isThereCrossMovement(n.cable, va, vb):
					continue
				newCable = tightenCable(n.cable, va, vb)
				l = Geom.lengthOfCurve(newCable)
				if l <= model.MAX_CABLE:
					child = Node(cable=newCable, parent=n)
					n.children.append(child)
					q.enqueue(child)
	return None

def isThereCrossMovement(cable, dest1, dest2):
	# I've also included the case where the polygon is not simple
	p = Polygon()
	for v in getLongCable(cable, dest1, dest2):
		p.push_back(convertToPoint(v))
	return not p.is_simple()

def isAtDestination(n) -> bool:
	return convertToPoint(n.cable[0]) == convertToPoint(model.robots[0].destination) and convertToPoint(n.cable[-1]) == convertToPoint(model.robots[-1].destination)
