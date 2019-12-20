from model.modelService import Model

model = Model()
SMALL_DISTANCE = 0.01


def convertToPoint(vert):
	"""
	Utility function that takes a Vertex or Point and returns a Point
	"""
	if hasattr(vert, 'loc'):
		return vert.loc
	return vert

def ptToStringId(pt):
	"""
	Use this method internally to obtain a unique Id for each point in this triangulation
	"""
	return '%d,%d' % (convertToPoint(pt).x(), convertToPoint(pt).y())

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
	prev = ptToStringId(verts[-1])
	for vert in verts:
		idStr = ptToStringId(vert)
		if prev != idStr:
			trimmed.append(vert)
			prev = idStr
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

def almostEqual(v1, v2) -> bool:
	pt1 = convertToPoint(v1)
	pt2 = convertToPoint(v2)
	vect = pt1 - pt2
	return vect.squared_length() < SMALL_DISTANCE

# I have copied this from GEOM because I can't import that file here
def getClosestVertex(pt):
	for v in model.robots:
		if almostEqual(pt, v):
			return v
		if almostEqual(pt, v.destination):
			return v.destination

	for v in model.vertices:
		if almostEqual(pt, v):
			return v
