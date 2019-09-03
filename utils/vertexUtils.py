from utils.cgal.types import convertToPoint

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
