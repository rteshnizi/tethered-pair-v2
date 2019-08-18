from typing import List
from model.vertex import Vertex

import utils.cgal.geometry as Geom
import utils.listUtils as ListUtils
from algorithm.gap import gapDetector
from model.modelService import Model
from algorithm.node import Node
from utils.priorityQ import PriorityQ
from algorithm.triangulation import Triangulation

model = Model()

VertList = List[Vertex]

def aStar():
	# newCable = tightenCable(model.cable, model.robots[0].destination, model.robots[1].destination)

	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	while not q.isEmpty():
		n: Node = q.dequeue()
		if isAtDestination(n):
			print("At Destination")
			return # For now terminate at first solution
		VA = gapDetector(n.cable[0], model.robots[0])
		VB = gapDetector(n.cable[-1], model.robots[-1])
		for va in VA:
			for vb in VB:
				newCable = tightenCable(n.cable, va.vrt, vb.vrt)
				l = Geom.lengthOfCurve(newCable)
				if l <= model.MAX_CABLE:
					child = Node(cable=newCable, parent=n)
					n.children.append(child)
					q.enqueue(child)

def isAtDestination(n) -> bool:
	return n.cable[0].name == model.robots[0].destination.name and n.cable[-1].name == model.robots[-1].destination.name

def tightenCable(cable: VertList, dest1: Vertex, dest2: Vertex) -> list:
	"""
	This is an altered version of
	"""
	boundingBox = [cable[0], cable[-1], dest2, dest1]
	tri = Triangulation(boundingBox)
	# Edge case where the two robots go to the same point and cable is not making contact
	if tri.triangleCount == 1:
		return [dest1, dest2]
	leftSidePts = []
	rightSidePts = []
	longCable = [dest1] + cable + [dest2]
	# We use this to maintain the funnel
	refPt = longCable[0]
	# We represent an edge by a python set to make checks easier
	currE = frozenset([longCable[0], longCable[1]])
	currTri = tri.getIncidentTriangles(currE)
	if len(currTri) != 1:
		raise RuntimeError("currTri must be incident to exactly 1 triangle for the first segment of the cable")
	currTri = next(iter(currTri)) # Get the only item in the set
	for i in range(1, len(longCable) - 1):
		e = frozenset([longCable[i], longCable[i + 1]])
		pivot = e & currE
		if len(pivot) != 1:
			raise RuntimeError("The intersection of e and currE must yield only 1 vertex")
		pivot = next(iter(pivot))
		tries = tri.getIncidentTriangles(e)
		while not tries & frozenset([currTri]):
			edges = tri.getIncidentEdges(pivot, currTri)
			flipEdge = edges - frozenset([currE])
			if len(flipEdge) != 1:
				raise RuntimeError("There must only be 1 flipEdge")
			flipEdge = next(iter(flipEdge))
			currTri = tri.getIncidentTriangles(flipEdge) - frozenset([currTri])
			if len(currTri) != 1:
				raise RuntimeError("flipEdge must be incident to exactly 2 triangles one of which is currTri")
			currTri = next(iter(currTri))
			refPt = addPointsToFunnel(leftSidePts, rightSidePts, flipEdge, refPt)
			currE = flipEdge
			# Debugging
			# tri.getCanvasEdge(currE).highlightEdge()
		currE = e
	# tri.getCanvasEdge(currE).highlightEdge()
	shorterSide = getShorterSideOfFunnel(leftSidePts, rightSidePts)
	shortCable = [dest1] + shorterSide + [dest2]
	return ListUtils.removeRepeatedVertsOrdered(shortCable)



def addPointsToFunnel(leftSideVrt: list, rightSideVrt: list, flipEdge: frozenset, refPt):
	"""
	Adds the flipEdge verts to the appropriate side list and returns midPoint of the flipEdge
	"""
	flipEdgeVerts = list(flipEdge)
	flipEdgeMid = Geom.midpoint(flipEdgeVerts[0], flipEdgeVerts[1])
	for vrt in flipEdge:
		if Geom.isColinear(refPt, flipEdgeMid, vrt):
			raise RuntimeError("flipEdge shouldn't be colinear")
		if Geom.isToTheRight(refPt, flipEdgeMid, vrt):
			appendIfNotRepeated(rightSideVrt, vrt)
		else:
			appendIfNotRepeated(leftSideVrt, vrt)
	return flipEdgeMid

def appendIfNotRepeated(vrtList, vrt):
	l = len(vrtList)
	if l == 0 or vrt.name != vrtList[l - 1].name:
		vrtList.append(vrt)


def getShorterSideOfFunnel(leftSidePts: list, rightSidePts: list) -> list:
	leftL = Geom.lengthOfCurve(leftSidePts)
	rightL = Geom.lengthOfCurve(rightSidePts)
	return leftSidePts if leftL < rightL else rightSidePts
