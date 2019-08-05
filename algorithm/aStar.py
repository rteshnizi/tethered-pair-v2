from algorithm.gap import gapDetector
from model.model_service import Model
from algorithm.node import Node
import utils.cgal.geometry as geometry
from utils.priorityQ import PriorityQ
from algorithm.triangulation import Triangulation

model = Model()

def aStar():
	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	n = q.dequeue()
	if (isAtDestination(n)):
		return # For now terminate at first solution
	# VA = gapDetector(n.cable[0], model.robots[0])
	# VB = gapDetector(n.cable[-1], model.robots[-1])
	# va = VA[0]
	# vb = VB[0]
	# newCable = tightenCable(n.cable, va.vrt, vb.vrt)
	newCable = tightenCable(n.cable, model.robots[0].destination, model.robots[1].destination)
	# while (not q.isEmpty()):
	# 	n = q.dequeue()
	# 	if (isAtDestination(n)):
	# 		return # For now terminate at first solution
	# 	VA = gapDetector(n.cable[0], model.robots[0])
	# 	VB = gapDetector(n.cable[-1], model.robots[-1])
	# 	for va in VA:
	# 		for vb in VB:
	# 			newCable = tightenCable(n.cable, va.vrt, vb.vrt)
	# 			if (not newCable):
	# 				continue


def isAtDestination(n):
	return n.cable[0].name == model.robots[0].destination.name and n.cable[-1].name == model.robots[-1].destination.name

def tightenCable(cable, dest1, dest2):
	boundingBox = [cable[0], cable[-1], dest2, dest1]
	tri = Triangulation(boundingBox, debug=True)
	# tri.eraseDrawnEdges()
	newCable = []
	return newCable
