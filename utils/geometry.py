from sympy.geometry.line import Segment

"""
Geometry Helper functions
"""

def vertexDistance(v1, v2):
	return v1.loc.distance(v2.loc)

def createSegmentFromVertices(v1, v2):
	return Segment(v1.loc, v2.loc)

def createPolygonFromVertices(verts):
	return Segment([v.loc for v in verts])
