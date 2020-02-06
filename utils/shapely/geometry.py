from utils.cgal.types import Point
from utils.vertexUtils import convertToPoint
from shapely.geometry import Polygon as SHPolygon, LineString as SHLineString, Point as SHPoint

def _getCoordinateList(verts):
	coords = []
	for v in verts:
		pt = convertToPoint(v)
		coord = (pt.x(), pt.y())
		coords.append(coord)
	return coords

def polygonIntersection(verts1, verts2):
	pts1 = _getCoordinateList(verts1)
	pts2 = _getCoordinateList(verts2)
	poly1 = SHPolygon(pts1)
	poly2 = SHPolygon(pts2)
	intersection = poly1.intersection(poly2)
	return [Point(*pt) for pt in intersection.exterior.coords]

def circleAndLineSegmentIntersection(pt1, pt2, center, radius):
	"""
	https://stackoverflow.com/a/30998492/750567
	"""
	linePts = _getCoordinateList([pt1, pt2])
	seg = SHLineString(linePts)
	cPt = convertToPoint(center)
	circle = SHPoint(cPt.x(), cPt.y()).buffer(radius).boundary
	SHintersection = circle.intersection(seg)
	if not isinstance(SHintersection, SHPoint):
		raise RuntimeError("Haven't debugged this yet")
	return Point(SHintersection.x, SHintersection.y)
