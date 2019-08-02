from algorithm.gap import gapDetector
from model.model_service import Model
from algorithm.node import Node
import utils.cgal.geometry as geometry
from utils.priorityQ import PriorityQ
from utils.cgal.triangulation import triangulate

model = Model()

def aStar():
	# triangulate([model.cable[0], model.cable[-1], model.robots[-1].destination, model.robots[0].destination], True)
	# reza = 0
	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	while (not q.isEmpty()):
		n = q.dequeue()
		if (isAtDestination(n)):
			return # For now terminate at first solution
		V_A = gapDetector(n.cable[0], model.robots[0])
		V_B = gapDetector(n.cable[-1], model.robots[-1])
		for va in V_A:
			for vb in V_B:
				newCable = tightenCable(n.cable, va.vrt, vb.vrt)
				if (not newCable):
					continue


def isAtDestination(n):
	return n.cable[0].name == model.robots[0].destination.name and n.cable[-1].name == model.robots[-1].destination.name

def tightenCable(cable, dest1, dest2):
	boundingBox = [cable[0], cable[-1], dest2, dest1]
	info = triangulate(boundingBox, True)
	if not info:
		return []
	newCable = []
	return newCable
