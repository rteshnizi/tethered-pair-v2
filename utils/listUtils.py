import utils.cgal.geometry as Geom

def _convertVertListToDict(verts: list) -> dict:
	vertDict = {}
	for vert in verts:
		vertDict[Geom.ptToStringId(vert)] = vert
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
	prev = None
	for vert in verts:
		if (not prev) or prev.name != vert.name:
			trimmed.append(vert)
			prev = vert
	return trimmed

def setSubtractPoints(verts1: list, verts2: list) -> list:
	d1 = _convertVertListToDict(verts1)
	d2 = _convertVertListToDict(verts2)
	l = [v for (k, v) in d1.items() if k not in d2]
	return l
