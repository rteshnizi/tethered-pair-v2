from typing import List
from model.vertex import Vertex

import utils.cgal.geometry as Geom
import utils.vertexUtils as VertexUtils
from algorithm.visibility import findGaps
from algorithm.node import Node
from algorithm.triangulation import Triangulation
from model.modelService import Model
from model.cable import Cable
from utils.priorityQ import PriorityQ
from utils.cgal.types import Point

model = Model()

VertList = List[Vertex]

def aStar():
	# newCable = tightenCable(model.cable, model.robots[0].destination, model.robots[1].destination, debug=True, runAlg=True)
	processReducedVisibilityGraph()
	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	while not q.isEmpty():
		n: Node = q.dequeue()
		if isAtDestination(n):
			print("At Destination")
			Cable(model.canvas, "CABLE", n.cable)
			return # For now terminate at first solution
		VA = findGaps(n.cable[0], model.robots[0])
		VB = findGaps(n.cable[-1], model.robots[-1])
		for va in VA:
			for vb in VB:
				# For now I deliberately avoid cross movement because it crashes the triangulation
				# In reality we can fix this by mirorring the space (like I did in the previous paper)
				if isThereCrossMovement(n.cable[0], va.vrt, n.cable[-1], vb.vrt):
					continue
				newCable = tightenCable(n.cable, va.vrt, vb.vrt)
				l = Geom.lengthOfCurve(newCable)
				if l <= model.MAX_CABLE:
					child = Node(cable=newCable, parent=n)
					n.children.append(child)
					q.enqueue(child)

def processReducedVisibilityGraph() -> None:
	# TODO: Here I should assign
	pass
	# for v in model.vertices:

def isThereCrossMovement(src1, dest1, src2, dest2):
	intersection = Geom.intersectSegmentAndSegment(src1, dest1, src2, dest2)
	if isinstance(intersection, Point):
		return True
	return False

def isAtDestination(n) -> bool:
	return n.cable[0].name == model.robots[0].destination.name and n.cable[-1].name == model.robots[-1].destination.name

def tightenCable(cable: VertList, dest1: Vertex, dest2: Vertex, debug=False, runAlg=True) -> list:
	"""
	This is an altered version of
	"""
	tri = Triangulation(cable[0], cable[-1], dest2, dest1, debug=debug)
	if not runAlg: return [] # For debugging only the triangulation
	# Edge case where the two robots go to the same point and cable is not making contact
	if tri.triangleCount == 1:
		return [dest1, dest2]
	leftSidePts = []
	rightSidePts = []
	longCable = [dest1] + cable + [dest2]
	# We use this to maintain the funnel
	refPt = longCable[0]
	# We represent an edge by a python set to make checks easier
	currE = getEdge(longCable[0], longCable[1])
	currTries = tri.getIncidentTriangles(currE)
	for i in range(1, len(longCable) - 1):
		e = getEdge(longCable[i], longCable[i + 1])
		pivot = e & currE
		if len(pivot) != 1:
			raise RuntimeError("The intersection of e and currE must yield only 1 vertex")
		pivot = next(iter(pivot))
		tries = tri.getIncidentTriangles(e)
		while not tries & currTries:
			(flipEdge, currTries) = getFlipEdgeAndCurrentTriangle(tri, pivot, currE, currTries, e)
			refPt = addPointsToFunnel(leftSidePts, rightSidePts, flipEdge, refPt)
			currE = flipEdge
			# Debugging
			# tri.getCanvasEdge(currE).highlightEdge()
		currTries = tries & currTries
		currE = e
		refPt = longCable[i]
	# tri.getCanvasEdge(currE).highlightEdge()
	shortCable = getShorterSideOfFunnel(dest1, dest2, leftSidePts, rightSidePts)
	return VertexUtils.removeNoNameMembers(VertexUtils.removeRepeatedVertsOrdered(shortCable))

def getEdge(vert1, vert2) -> frozenset:
	# We need to do this because the triangulation only recognizes the vertices that are registered by location in the model
	# we have repeated vertices and the triangulation might have chosen the other vertex
	v1 = model.getVertexByLocation(vert1.loc.x(), vert1.loc.y())
	v2 = model.getVertexByLocation(vert2.loc.x(), vert2.loc.y())
	# We represent an edge by a python set to make checks easier
	return makeFrozenSet([v1, v2])


def makeFrozenSet(members):
	if isinstance(members, list):
		return frozenset(members)
	# Assume none-iterable item, therefore it's a single item
	return frozenset([members])

def getFlipEdgeAndCurrentTriangle(cgalTriangulation, pivot, currE: frozenset, currTries: frozenset, targetE: frozenset):
	# In case there are multiple currTries
	# flipEdge is the one that falls between currEdge and targetEdge
	pivotSet = makeFrozenSet(pivot)
	otherPointOnTargetE = next(iter(targetE - pivotSet))
	otherEndOfCrrE = next(iter(currE - pivotSet))
	targetEdgeIsToTheRight = Geom.isToTheRight(pivot, otherEndOfCrrE, otherPointOnTargetE)
	for tri in currTries:
		edges = cgalTriangulation.getIncidentEdges(pivot, tri)
		e = edges - makeFrozenSet(currE)
		if e:
			if len(e) != 1:
				raise RuntimeError("There must only be 1 flipEdge")
			e = next(iter(e))
			otherEndOfE = next(iter(e - pivotSet))
			# If e doesn't fall between currE and targetE, then this is not the flip edge
			if Geom.isToTheRight(pivot, otherEndOfCrrE, otherEndOfE) != targetEdgeIsToTheRight: continue
			incident = cgalTriangulation.getIncidentTriangles(e)
			triangle = incident - currTries
			if not triangle: continue
			flipEdge = e
			currTries = triangle
			break
	if len(currTries) != 1:
		raise RuntimeError("flipEdge must be incident to exactly 2 triangles one of which is currTri")
	return (flipEdge, currTries)


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
			VertexUtils.appendIfNotRepeated(rightSideVrt, vrt)
		else:
			VertexUtils.appendIfNotRepeated(leftSideVrt, vrt)
	return flipEdgeMid

def getShorterSideOfFunnel(src, dst, leftSidePts: list, rightSidePts: list) -> list:
	"""
	Params
	===
	src: Source point of the funnel

	dst: Destination point of the funnel
	"""
	lCable = [src] + leftSidePts + [dst]
	rCable = [src] + rightSidePts + [dst]
	leftL = Geom.lengthOfCurve(lCable)
	rightL = Geom.lengthOfCurve(rCable)
	return lCable if leftL < rightL else rCable
