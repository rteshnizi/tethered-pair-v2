import utils.cgal.geometry as Geom
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.visibility import findGaps
from algorithm.node import Node
from algorithm.cableAlgorithms import tightenCable
from model.modelService import Model
from utils.priorityQ import PriorityQ
from utils.cgal.types import Polygon

model = Model()

def aStar() -> Node:
	processReducedVisibilityGraph()
	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	while not q.isEmpty():
		n: Node = q.dequeue()
		if isAtDestination(n):
			print("At Destination")
			return n # For now terminate at first solution
		VA = findGaps(n.cable[0], model.robots[0])
		VB = findGaps(n.cable[-1], model.robots[-1])
		for va in VA:
			for vb in VB:
				# For now I deliberately avoid cross movement because it crashes the triangulation
				# In reality we can fix this by mirorring the space (like I did in the previous paper)
				if isThereCrossMovement(n.cable, va.vrt, vb.vrt):
					continue
				newCable = tightenCable(n.cable, va.vrt, vb.vrt)
				l = Geom.lengthOfCurve(newCable)
				if l <= model.MAX_CABLE:
					child = Node(cable=newCable, parent=n)
					n.children.append(child)
					q.enqueue(child)
	return None

def processReducedVisibilityGraph() -> None:
	# TODO: Here I should assign
	pass
	# for v in model.vertices:

def isThereCrossMovement(cable, dest1, dest2):
	# I've also included the case where the polygon is not simple
	p = Polygon()
	p.push_back(convertToPoint(dest1))
	for v in cable:
		p.push_back(convertToPoint(v))
	p.push_back(convertToPoint(dest2))
	return not p.is_simple()

def isAtDestination(n) -> bool:
	return n.cable[0].name == model.robots[0].destination.name and n.cable[-1].name == model.robots[-1].destination.name
