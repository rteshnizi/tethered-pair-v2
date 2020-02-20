import math
from model.modelService import Model, ptToStringId as _ptToStringId

model = Model()
SMALL_DISTANCE = 1 # in pixels

def convertToPoint(vert):
	"""
	Utility function that takes a Vertex or Point and returns a Point
	"""
	if hasattr(vert, 'loc'):
		return vert.loc
	return vert

def ptToStringId(vert):
	return _ptToStringId(convertToPoint(vert))

def _convertVertListToDict(verts: list) -> dict:
	vertDict = {}
	for vert in verts:
		vertDict[ptToStringId(vert)] = vert
	return vertDict

def removeRepeatedVertsUnordered(verts: list) -> list:
	"""
	Takes a list (unordered) of Vertex and removes items that are sequentially repeated

	NOTE: The order of the elements might change
	"""
	vertDict = _convertVertListToDict(verts)
	return list(vertDict.values())

def removeRepeatedVertsOrdered(verts: list) -> list:
	"""
	Takes a list (ordered) of Vertex and removes items that are sequentially repeated
	"""
	trimmed = []
	# FIXME: For the lif of me, I don't know what's the logic behind making the list circular. Maybe there is a point to it?
	# prev = ptToStringId(verts[-1])
	prevId = ""
	for vert in verts:
		idStr = ptToStringId(vert)
		if prevId != idStr:
			trimmed.append(vert)
			prevId = idStr
	return trimmed

def removeNoNameMembers(verts: list) -> list:
	trimmed = []
	for i in range(len(verts)):
		try:
			name = verts[i].name
			trimmed.append(verts[i])
		except AttributeError:
			pass
	return trimmed

def appendIfNotRepeated(vrtList, vrt):
	l = len(vrtList)
	if l == 0 or ptToStringId(vrt) != ptToStringId(vrtList[l - 1]):
		vrtList.append(vrt)

def setSubtractPoints(verts1: list, verts2: list) -> list:
	d1 = _convertVertListToDict(verts1)
	d2 = _convertVertListToDict(verts2)
	l = [v for (k, v) in d1.items() if k not in d2]
	return l

def almostEqual(v1, v2) -> tuple:
	"""
	Checks if 2 points/vertices are equal with a small margin of error.

	Returns
	=====
	A Tuple (bool, float) where:
	* the bool indicates if the 2 points are the margin of error away from each other
	* the float is the
	"""
	pt1 = convertToPoint(v1)
	pt2 = convertToPoint(v2)
	vect = pt1 - pt2
	l = math.sqrt(vect.squared_length())
	return (l < SMALL_DISTANCE, l)

def _getClosestVertex(pt):
	candidate = None
	minDist = 100000000000
	for v in model.robots:
		eq, dist = almostEqual(pt, v)
		if eq and dist < minDist:
			candidate = v
			minDist = dist
			if dist == 0: return candidate
		eq, dist = almostEqual(pt, v.destination)
		if eq and dist < minDist:
			candidate = v.destination
			minDist = dist
			if dist == 0: return candidate

	for v in model.vertices:
		eq, dist = almostEqual(pt, v)
		if eq and dist < minDist:
			candidate = v
			minDist = dist
			if dist == 0: return candidate
	return candidate

def getClosestVertex(pt):
	candidate = None
	for v in model.robots:
		eq, dist = almostEqual(pt, v)
		if eq:
			candidate = v
			if dist == 0: return candidate
		eq, dist = almostEqual(pt, v.destination)
		if eq:
			candidate = v.destination
			if dist == 0: return candidate

	for v in model.vertices:
		eq, dist = almostEqual(pt, v)
		if eq:
			candidate = v
			if dist == 0: return candidate

	# For temp vertices we actually want equality
	for tempVert in model.tempVertices.values():
		if convertToPoint(pt) == convertToPoint(tempVert):
			return tempVert
	return candidate
