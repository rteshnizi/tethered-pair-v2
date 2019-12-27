from typing import List
from model.vertex import Vertex
import utils.cgal.geometry as Geom
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.visibility import applyMovement
from algorithm.triangulation import Triangulation
from algorithm.funnel import Funnel
from model.modelService import Model

model = Model()

VertList = List[Vertex]

def testTightenCable(debugTri=False):
	return tightenCable(model.cable, model.robots[0].destination, model.robots[1].destination, debugTri)

def tightenCable(cable: VertList, dest1: Vertex, dest2: Vertex, debugTri=False) -> VertList:
	"""
	This is an altered version of "Hershberger, J., & Snoeyink, J. (1994). Computing minimum length paths of a given homotopy class."

	https://doi.org/10.1016/0925-7721(94)90010-8
	"""
	(cable, dest1, dest2) = pushCableAwayFromObstacles(cable, dest1, dest2)
	tri = Triangulation(cable, dest1, dest2, debug=debugTri)
	# Edge case where the two robots go to the same point and cable is not making contact
	if tri.triangleCount == 1:
		return [dest1, dest2]
	allCurrentTries = []
	longCable = getLongCable(cable, dest1, dest2)
	if len(longCable) == 2: return [getClosestVertex(pt) for pt in longCable]
	# We represent an edge by a python set to make checks easier
	currE = getEdge(longCable[0], longCable[1])
	currTri = tri.getIncidentTriangles(currE)
	if len(currTri) != 1:
		# randomly pick one. If this is the wrong triangle, the pivot algorithm will fix itself.
		# However, the resulting sleeve will have repeated triangles. This will be taken care of in findSleeve()
		# FIXME: Needs testing
		currTri = frozenset([next(iter(currTri))])
		# for t in currTries:
		# 	currTries = getTrueInitTri(currE, getEdge(longCable[1], longCable[2]), frozenset([t]), tri)
		# 	if len(currTries) == 1:
		# 		break
		# 	else:
		# 		raise RuntimeError("I don't want to live on this planet anymore.")
	for i in range(1, len(longCable) - 1):
		allCurrentTries.append(currTri)
		e = getEdge(longCable[i], longCable[i + 1])
		pivot = e & currE
		if len(pivot) != 1:
			raise RuntimeError("The intersection of e and currE must yield only 1 vertex")
		pivot = next(iter(pivot))
		tries = tri.getIncidentTriangles(e)
		while not tries & currTri:
			(flipEdge, currTri) = getFlipEdgeAndCurrentTriangle(tri, pivot, currE, currTri, tries)
			if flipEdge: currE = flipEdge
			# FIXME: This happens if the dest1 + cable + dest2 is not a simple polygon
			else: raise RuntimeError("Deal with this at some point.")
			allCurrentTries.append(currTri)
			# Debugging
			# tri.getCanvasEdge(currE).highlightEdge()
		currTri = tries & currTri
		currE = e
	sleeve = findSleeve(allCurrentTries)
	return getShortestPath(tri, dest1, dest2, sleeve)

def pushCableAwayFromObstacles(cable: VertList, dest1: Vertex, dest2: Vertex) -> tuple:
	transformed = [dest1] + cable + [dest2]
	for i in range(len(transformed)):
		c = transformed[i]
		for o in model.obstacles:
			for v in o.vertices:
				if convertToPoint(v) != convertToPoint(c): continue
				vects = [Geom.getEpsilonVector(n, v) for n in v.adjacentOnObstacle]
				if len(vects) != 2: raise RuntimeError("There should only be 2 adjacent vertices to any vertex")
				epsVect = Geom.getEpsilonVectorFromVect(vects[0] + vects[1])
				pushedC = convertToPoint(c) + epsVect
				transformed[i] = pushedC
	return (transformed[1:-1], transformed[0], transformed[-1])

def getTrueInitTri(currE, targetEdge, currTri, tri: Triangulation):
	"""
	This modified pivot algorithm. It pivots the triangles until we either meet the target edge or not.
	The one that meets the target edge is the tru initial triangle.
	"""
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
	if convertToPoint(cable[1]) == convertToPoint(dest1) and convertToPoint(cable[-2]) == convertToPoint(dest2):
		copy = cable[1:-1]
		copy[0] = dest1
		copy[-1] = dest2
		return copy
	if convertToPoint(cable[1]) == convertToPoint(dest1):
		copy = cable[1:]
		copy.append(dest2)
		copy[0] = dest1
		return copy
	if convertToPoint(cable[-2]) == convertToPoint(dest2):
		copy = cable[:-1]
		copy.insert(0, dest1)
		copy[-1] = dest2
		return copy
	return [dest1] + cable + [dest2]

def getEdge(vert1, vert2) -> frozenset:
	# FIXME: This has changed now. We push the cable away from the obstacles
	# We need to do this because the triangulation only recognizes the vertices that are registered by location in the model
	# we have repeated vertices and the triangulation might have chosen the other vertex
	# v1 = model.getVertexByLocation(vert1.loc.x(), vert1.loc.y())
	# v2 = model.getVertexByLocation(vert2.loc.x(), vert2.loc.y())
	# We represent an edge by a python set to make checks easier
	# return makeFrozenSet([v1, v2])
	return makeFrozenSet([vert1, vert2])

def areEdgesEqual(e1 ,e2) -> bool:
	e1 = [convertToPoint(pt) for pt in e1]
	e2 = [convertToPoint(pt) for pt in e2]
	e1 = frozenset(e1)
	e2 = frozenset(e2)
	return e1 == e2

def makeFrozenSet(members):
	if isinstance(members, list):
		return frozenset(members)
	# Assume none-iterable item, therefore it's a single item
	return frozenset([members])

def getFlipEdgeAndCurrentTriangle(cgalTriangulation: Triangulation, pivot, currE: frozenset, currTries: frozenset, candidates=frozenset()):
	if len(currTries) > 1:
		raise RuntimeError("There must only be 1 currTries")
	# Check if the currentEdge is actually the flip edge.
	# That would be the case if the target triangle and currentTriangle have an edge in common which is currE
	tri = next(iter(currTries))
	for candidate in candidates:
		e = cgalTriangulation.getCommonEdge(tri, candidate)
		if areEdgesEqual(e, currE): return (currE, makeFrozenSet(candidate))
	# FlipEdge wasn't the currentEdge, so we move on
	edges = cgalTriangulation.getIncidentEdges(pivot, tri)
	e = edges - makeFrozenSet(currE)
	if e:
		if len(e) != 1:
			raise RuntimeError("There must only be 1 flipEdge")
		e = next(iter(e))
		# I don't think currTries will ever be greater than 1, so I commented the above code and replaced it with an exception at the top
		# if len(currTries) > 1:
			# Test the epsilon push thing
			# otherEndOfE = next(iter(e - { pivot }))
			# epsilon = Geom.getEpsilonVector(pivot, otherEndOfE)
			# # If e doesn't fall between currE and targetE, then this is not the flip edge
			# if not cgalTriangulation.isPointInsideOriginalPolygon(pivot.loc + epsilon): continue
		incident = cgalTriangulation.getIncidentTriangles(e)
		triangle = incident - currTries
		# This happens when the polygon formed by the cable and destinations is not simple
		if not triangle:
			# We have chosen the wrong flipEdge
			e = currE
			incident = cgalTriangulation.getIncidentTriangles(e)
			triangle = incident - currTries
		flipEdge = e
		currTries = triangle
	if len(currTries) != 1:
		raise RuntimeError("flipEdge must be incident to exactly 2 triangles one of which is currTri")
	return (flipEdge, currTries)

def findSleeve(allTries: list):
	"""
	Simply removes repeated triangles from the list. It relies on CGAL for equality of triangles.
	"""
	# First get rid of the frozensets
	allTries = [next(iter(t)) for t in allTries]
	# Remove consecutively repeated triangles
	trimmed = []
	for tri in allTries:
		if len(trimmed) > 0 and trimmed[-1] == tri: continue
		trimmed.append(tri)
	# Remove palindromes
	allTries = trimmed
	trimmed = []
	for tri in allTries:
		if len(trimmed) > 1 and trimmed[-2] == tri:
			trimmed.pop()
		else:
			trimmed.append(tri)

	# triIndices = {}
	# trimmed = []
	# for i in range(len(allTries)):
	# 	tri = allTries[i]
	# 	if tri not in triIndices:
	# 		triIndices[tri] = i
	# 		trimmed.append(tri)
	# 	else:
	# 		trimmed = trimmed[:triIndices[tri] + 1]

	return trimmed

def getShortestPath(tri: Triangulation, src: Vertex, dst: Vertex, sleeve: list):
	# We need to do this because the funnel algorithm assumes that the path lies inside the triangulation
	if len(sleeve) == 0:
		raise RuntimeError("Here we are.")
	funnel = Funnel(src, tri, sleeve)
	pathPt = funnel.getShortestPath(dst)
	pathVt = [getClosestVertex(pt) for pt in pathPt]
	pathVt = removeRepeatedVertsOrdered(pathVt)
	return pathVt

def tightenCableClassic(cable: VertList, dest1: Vertex, dest2: Vertex, debug=False, runAlg=True) -> VertList:
	cable = applyMovement(cable, dest1, True)
	return applyMovement(cable, dest2, False)
