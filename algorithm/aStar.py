from typing import List
from model.vertex import Vertex

from algorithm.gap import gapDetector
from model.model_service import Model
from algorithm.node import Node
import utils.cgal.geometry as geometry
from utils.priorityQ import PriorityQ
from algorithm.triangulation import Triangulation

model = Model()

VertList = List[Vertex]

def aStar():
	newCable = tightenCable(model.cable, model.robots[0].destination, model.robots[1].destination)

	# q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	# root = Node(cable=model.cable)
	# q.enqueue(root)
	# n = q.dequeue()
	# if (isAtDestination(n)):
	# 	return # For now terminate at first solution
	# VA = gapDetector(n.cable[0], model.robots[0])
	# VB = gapDetector(n.cable[-1], model.robots[-1])
	# va = VA[0]
	# vb = VB[0]
	# newCable = tightenCable(n.cable, va.vrt, vb.vrt)

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

def tightenCable(cable: VertList, dest1: Vertex, dest2: Vertex) -> list:
	boundingBox = [cable[0], cable[-1], dest2, dest1]
	tri = Triangulation(boundingBox, debug=True)
	funnel = [dest1]
	longCable = [dest1] + cable + [dest2]
	shortCable = [dest1]
	# We represent an edge by a python set to make checks easier
	currE = frozenset([longCable[0], longCable[1]])
	currTri = tri.getIncidentTriangles(currE)
	if (len(currTri) != 1):
		raise RuntimeError("currTri must be incident to exactly 1 triangle for the first segment of the cable")
	currTri = next(iter(currTri)) # Get the only item in the set
	for i in range(1, len(longCable) - 1):
		e = frozenset([longCable[i], longCable[i + 1]])
		pivot = e & currE
		if (len(pivot) != 1):
			raise RuntimeError("The intersection of e and currE must yield only 1 vertex")
		pivot = next(iter(pivot))
		tries = tri.getIncidentTriangles(e)
		while (not tries & frozenset([currTri])):
			edges = tri.getIncidentEdges(pivot, currTri)
			flipEdge = edges - frozenset([currE])
			if (len(flipEdge) != 1):
				raise RuntimeError("There must only be 1 flipEdge")
			flipEdge = next(iter(flipEdge))
			currTri = tri.getIncidentTriangles(flipEdge) - frozenset([currTri])
			if (len(currTri) != 1):
				raise RuntimeError("flipEdge must be incident to exactly 2 triangles one of which is currTri")
			currTri = next(iter(currTri))
			currE = flipEdge
			_cgalEdge = tri.getCgalEdge(currE)
			tri.getCanvasEdge(currE).highlightEdge()
			funnel
		currE = e
	shortCable.append(dest2)
	return shortCable

def addPointsToFunnel(funnel, pts: frozenset, segment):
	# TODO: CONTINUE HERE
	pass
