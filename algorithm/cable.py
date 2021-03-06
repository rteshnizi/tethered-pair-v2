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

def tightenCable(cable: VertList, destA: Vertex, destB: Vertex, debugTri=False) -> VertList:
	"""
	Here we force the sleeve to be made up of the triangles to the left and to the right of the edges.
	Whichever leads to a shorter path we accept that one.
	"""
	cableCopy = cable[:] # The method mutates the list object
	pl = _tightenCable(cableCopy, destA, destB, True, debugTri)
	cableCopy = cable[:] # The method mutates the list object
	pr = _tightenCable(cableCopy, destA, destB, False, False) # only one of them should print the triangulation edges
	return pl if Geom.lengthOfCurve(pl) < Geom.lengthOfCurve(pr) else pr

def _tightenCable(cable: VertList, destA: Vertex, destB: Vertex, isLeft:bool, debugTri=False) -> VertList:
	"""
	This is an altered version of "Hershberger, J., & Snoeyink, J. (1994). Computing minimum length paths of a given homotopy class."

	https://doi.org/10.1016/0925-7721(94)90010-8
	"""
	(cable, destA, destB) = preprocessTheCable(cable, destA, destB)
	(cable, destA, destB) = pushCableAwayFromObstacles(cable, destA, destB)
	longCable = getLongCable(cable, destA, destB)
	if len(longCable) == 2: return [getClosestVertex(pt) for pt in longCable]
	longCable = removeRepeatedVertsOrdered(longCable)
	if len(longCable) == 2: return [getClosestVertex(pt) for pt in longCable]
	tri = Triangulation(cable, destA, destB, debug=debugTri)
	# Edge case where the two robots go to the same point and cable is not making contact
	if tri.triangleCount == 1:
		return [getClosestVertex(pt) for pt in [destA, destB]]
	allCurrentTries = []
	# We represent an edge by a python set to make checks easier
	currE = getEdge(longCable[0], longCable[1])
	currTri = tri.getIncidentTriangles(currE)
	currTri = chooseTriangleBySide(longCable[0], longCable[1], currTri, isLeft)
	for i in range(1, len(longCable) - 1):
		allCurrentTries.append(currTri)
		e = getEdge(longCable[i], longCable[i + 1])
		pivot = e & currE
		if len(pivot) != 1:
			raise RuntimeError("The intersection of e and currE must yield only 1 vertex")
		pivot = next(iter(pivot))
		tries = tri.getIncidentTriangles(e)
		tries = chooseTriangleBySide(longCable[i], longCable[i + 1], tries, isLeft)
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
	return getShortestPath(tri, destA, destB, sleeve)

def chooseTriangleBySide(v1, v2, tries, pickLeft):
	if len(tries) == 1: return tries
	isOnTheCorrectSide = Geom.isToTheLeft if pickLeft else Geom.isToTheRight
	for tri in tries:
		pts = [tri.vertex(i).point() for i in [0, 1, 2]]
		center = Geom.centroid(pts)
		if isOnTheCorrectSide(v1, v2, center): return frozenset({tri})
	raise RuntimeError("Weird! Right?")

def preprocessTheCable(cable: VertList, destA: Vertex, destB: Vertex) -> tuple:
	"""
	If moves are happening along the current cable
	"""
	if convertToPoint(destB) == convertToPoint(cable[-2]) or Geom.isCollinear(cable[-2], cable[-1], destB):
		cable[-1] = destB
	if convertToPoint(destA) == convertToPoint(cable[1]) or Geom.isCollinear(cable[1], cable[0], destA):
		cable[0] = destA
	cable = removeRepeatedVertsOrdered(cable)
	return (cable, destA, destB)

def pushCableAwayFromObstacles(cable: VertList, destA: Vertex, destB: Vertex) -> tuple:
	transformed = [destA] + cable + [destB]
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
	if len(cable) == 0:
		return [dest1, dest2]
	# We now check for collinearity in preprocessTheCable(), so the below code should be irrelevant
	# if convertToPoint(cable[1]) == convertToPoint(dest1) and convertToPoint(cable[-2]) == convertToPoint(dest2):
	# 	copy = cable[1:-1]
	# 	if len(copy) == 0:
	# 		copy.append(dest1)
	# 		copy.append(dest2)
	# 	else:
	# 		copy[0] = dest1
	# 		copy[-1] = dest2
	# 	return copy
	# if convertToPoint(cable[1]) == convertToPoint(dest1):
	# 	copy = cable[1:]
	# 	copy.append(dest2)
	# 	copy[0] = dest1
	# 	return copy
	# if convertToPoint(cable[-2]) == convertToPoint(dest2):
	# 	copy = cable[:-1]
	# 	copy.insert(0, dest1)
	# 	copy[-1] = dest2
	# 	return copy
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
		# FIXME: Why is there still edges that fall inside an obstacle? Run case.json and you'll see
		# For very rare edge case where there are still edges that fall inside an obstacle
		# This fix assumes convex obstacles
		if len(e) != 1:
			eList = []
			for edge in e:
				inObstacle = False
				for o in model.obstacles:
					verts = list(edge)
					mid = Geom.midpoint(verts[0], verts[1])
					if o.enclosesPoint(mid):
						inObstacle = True
						break
				if not inObstacle: eList.append(edge)
			e = frozenset(eList)
		# This is for error detection, don't delete this, it's not related to the above bug fix
		if len(e) != 1:
			cgalTriangulation.drawEdges()
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

def getShortestPath(tri: Triangulation, dest1: Vertex, dest2: Vertex, sleeve: list):
	# We need to do this because the funnel algorithm assumes that the path lies inside the triangulation
	if len(sleeve) == 0:
		raise RuntimeError("Here we are.")
	funnel = Funnel(dest1, tri, sleeve)
	pathPt = funnel.getShortestPath(dest2)
	pathVt = [getClosestVertex(pt) for pt in pathPt]
	pathVt = removeRepeatedVertsOrdered(pathVt)
	if len(pathVt) < 2: return [getClosestVertex(dest1), getClosestVertex(dest2)]
	return pathVt

def tightenCableClassic(cable: VertList, dest1: Vertex, dest2: Vertex, debug=False, runAlg=True) -> VertList:
	cable = applyMovement(cable, dest1, True)
	return applyMovement(cable, dest2, False)
