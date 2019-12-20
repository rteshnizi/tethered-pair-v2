from utils.cgal.types import Point
from utils.vertexUtils import convertToPoint
from shapely.geometry import Polygon as SHPolygon

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
