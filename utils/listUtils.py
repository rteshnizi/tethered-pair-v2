def removeRepeatedVertsUnordered(verts: list) -> list:
	"""
	Takes a list (unordered) of Vertex and removes items that are sequentially repeated

	NOTE: The order of the elements might change
	"""
	vertDict = {}
	for vert in verts:
		vertDict[vert.name] = vert
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
