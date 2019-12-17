from typing import List
from model.vertex import Vertex
import utils.cgal.geometry as Geom
import utils.vertexUtils as VertexUtils
from algorithm.visibility import findGaps, applyMovement
from algorithm.node import Node
from algorithm.triangulation import Triangulation
from algorithm.funnel import Funnel
from model.modelService import Model
from model.cable import Cable
from utils.priorityQ import PriorityQ
from utils.cgal.types import Point, Polygon, convertToPoint

model = Model()

VertList = List[Vertex]

def aStar() -> None:
	print(tightenCable(model.cable, model.robots[0].destination, model.robots[1].destination, debug=True, runAlg=False))
	return
	processReducedVisibilityGraph()
	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	while not q.isEmpty():
		n: Node = q.dequeue()
		if isAtDestination(n):
			print("At Destination")
			c = Cable(model.canvas, "CABLE-D", n.cable)
			model.entities[c.name] = c
			print(n)
			return # For now terminate at first solution
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

def tightenCableClassic(cable: VertList, dest1: Vertex, dest2: Vertex, debug=False) -> VertList:
	cable = applyMovement(cable, dest1, True)
	return applyMovement(cable, dest2, False)

def tightenCable(cable: VertList, dest1: Vertex, dest2: Vertex, debug=False, runAlg=True) -> VertList:
	"""
	This is an altered version of "Hershberger, J., & Snoeyink, J. (1994). Computing minimum length paths of a given homotopy class."

	https://doi.org/10.1016/0925-7721(94)90010-8
	"""
	tri = Triangulation(cable, dest2, dest1, debug=debug)
	if not runAlg: return [] # For debugging only the triangulation
	# Edge case where the two robots go to the same point and cable is not making contact
	if tri.triangleCount == 1:
		return [dest1, dest2]
	leftSidePts = []
	rightSidePts = []
	flipEdges = []
	allCurrentTries = []
	changeOrientation = False
	longCable = getLongCable(cable, dest1, dest2)
	# We use this to maintain the funnel
	refPt = longCable[0]
	# We represent an edge by a python set to make checks easier
	currE = getEdge(longCable[0], longCable[1])
	currTries = tri.getIncidentTriangles(currE)
	if len(currTries) != 1:
		for t in currTries:
			currTries = getTrueInitTri(currE, getEdge(longCable[1], longCable[2]), frozenset([t]), tri)
			if len(currTries) == 1:
				break
			else:
				raise RuntimeError("I don't want to live on this planet anymore.")
	startTri = next(iter(currTries))
	for i in range(1, len(longCable) - 1):
		e = getEdge(longCable[i], longCable[i + 1])
		pivot = e & currE
		if len(pivot) != 1:
			raise RuntimeError("The intersection of e and currE must yield only 1 vertex")
		pivot = next(iter(pivot))
		tries = tri.getIncidentTriangles(e)
		allCurrentTries.append(currTries)
		while not tries & currTries:
			(flipEdge, currTries) = getFlipEdgeAndCurrentTriangle(tri, pivot, currE, currTries)
			if flipEdge:
				refPt = _addPointsToFunnel(leftSidePts, rightSidePts, flipEdge, refPt, changeOrientation)
				currE = flipEdge
			# FIXME: This happens if the dest1 + cable + dest2 is not a simple polygon
			else:
				changeOrientation = True
				leftSidePts.append(pivot)
				rightSidePts.append(pivot)
				currTries = tries
				flipEdge = e
			flipEdges.append(flipEdge)
			allCurrentTries.append(currTries)
			# Debugging
			# tri.getCanvasEdge(currE).highlightEdge()
		currTries = tries & currTries
		currE = e
		refPt = longCable[i]
		allCurrentTries.append(currTries)
	# tri.getCanvasEdge(currE).highlightEdge()
	graph = buildTriangleGraph(tri, allCurrentTries)
	sleeve = []
	findSleeve(tri, graph, startTri, dest2, set(), sleeve)
	return getShortestPath(tri, dest1, dest2, sleeve)

def getTrueInitTri(currE, targetEdge, currTri, tri: Triangulation):
	pivot = currE & targetEdge
	if len(pivot) != 1:
		raise RuntimeError("The intersection of e and currE must yield only 1 vertex")
	pivot = next(iter(pivot))
	tries = tri.getIncidentTriangles(currE)
	while not tries & currTri:
		(flipEdge, currTri) = getFlipEdgeAndCurrentTriangle(tri, pivot, currE, currTri)
	return tries & currTri

def getLongCable(cable: VertList, dest1: Vertex, dest2: Vertex) -> VertList:
	# FIXME: Check for colinearity instead of exact location
	if cable[1].loc == dest1.loc and cable[-2].loc == dest2.loc:
		copy = cable[1:-1]
		copy[0] = dest1
		copy[-1] = dest2
		return copy
	if cable[1].loc == dest1.loc:
		copy = cable[1:]
		copy.append(dest2)
		copy[0] = dest1
		return copy
	if cable[-2].loc == dest2.loc:
		copy = cable[:-1]
		copy.insert(0, dest1)
		copy[-1] = dest2
		return copy
	return [dest1] + cable + [dest2]

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

def getFlipEdgeAndCurrentTriangle(cgalTriangulation: Triangulation, pivot, currE: frozenset, currTries: frozenset):
	# In case there are multiple currTries flipEdge is the one that falls between currEdge and targetEdge.
	# That is, if we push the pivot epsilon in the direction of the candidate for flipEdge,
	# that point falls inside the original bounding box.
	for tri in currTries:
		edges = cgalTriangulation.getIncidentEdges(pivot, tri)
		e = edges - makeFrozenSet(currE)
		if e:
			if len(e) != 1:
				raise RuntimeError("There must only be 1 flipEdge")
			e = next(iter(e))
			if len(currTries) > 1:
				# Test the epsilon push thing
				otherEndOfE = next(iter(e - { pivot }))
				epsilon = Geom.getEpsilonVector(pivot, otherEndOfE)
				# If e doesn't fall between currE and targetE, then this is not the flip edge
				if not cgalTriangulation.isPointInsideOriginalPolygon(pivot.loc + epsilon): continue
			incident = cgalTriangulation.getIncidentTriangles(e)
			triangle = incident - currTries
			# This happens when the polygon formed by the cable and destinations is not simple
			if not triangle: return (None, None)
			flipEdge = e
			currTries = triangle
			break
	if len(currTries) != 1:
		raise RuntimeError("flipEdge must be incident to exactly 2 triangles one of which is currTri")
	return (flipEdge, currTries)

def _addPointsToFunnel(leftSideVrt: list, rightSideVrt: list, flipEdge: frozenset, refPt, changeOrientation: bool):
	"""
	Adds the flipEdge verts to the appropriate side list and returns midPoint of the flipEdge

	If change orientation is true, it means the polygon is not simple and thus we have to change the orientation of left and right from that point on.
	"""
	flipEdgeVerts = list(flipEdge)
	flipEdgeMid = Geom.midpoint(flipEdgeVerts[0], flipEdgeVerts[1])
	for vrt in flipEdge:
		if Geom.isColinear(refPt, flipEdgeMid, vrt):
			raise RuntimeError("flipEdge shouldn't be colinear")
		if Geom.isToTheRight(refPt, flipEdgeMid, vrt):
			if not changeOrientation:
				# Do it the normal way
				VertexUtils.appendIfNotRepeated(rightSideVrt, vrt)
			else:
				# Flip orientation
				VertexUtils.appendIfNotRepeated(leftSideVrt, vrt)
		else:
			if not changeOrientation:
				# Do it the normal way
				VertexUtils.appendIfNotRepeated(leftSideVrt, vrt)
			else:
				# Flip orientation
				VertexUtils.appendIfNotRepeated(rightSideVrt, vrt)
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

def buildTriangleGraph(tri: Triangulation, allTries: list):
	graph = {}
	for i in range(len(allTries)):
		this = allTries[i]
		for j in range(i + 1, len(allTries)):
			that = allTries[j]
			for t1 in this:
				for t2 in that:
					if tri.areTrianglesNeighbor(t1, t2):
						if t1 in graph:
							graph[t1].add(t2)
						else:
							graph[t1] = {t2}
						if t2 in graph:
							graph[t2].add(t1)
						else:
							graph[t2] = {t1}
	return graph

def findSleeve(tri: Triangulation, graph: dict, startTriangle, dest: Vertex, visited: set, sleeve: list):
	if tri.triangleHasVertex(startTriangle, dest):
		sleeve.insert(0, startTriangle)
		return True
	visited.add(startTriangle)
	if not graph.get(startTriangle):
		raise RuntimeError("Debug this")
	for child in graph[startTriangle]:
		if child in visited: continue
		if findSleeve(tri, graph, child, dest, visited, sleeve):
			sleeve.insert(0, startTriangle)
			return True
	return False

def getShortestPath(tri: Triangulation, src: Vertex, dst: Vertex, sleeve: list):
	# We need to do this because the funnel algorithm assumes that the path lies inside the triangulation
	if len(sleeve) == 0:
		raise RuntimeError("Here we are.")
	funnel = Funnel(src, tri, sleeve)
	path = funnel.getShortestPath(dst)
	path = [model.getVertexByLocation(pt.x(), pt.y()) for pt in path]
	return path
