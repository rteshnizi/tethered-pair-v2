from sympy.geometry.point import Point
from sympy.geometry.polygon import Polygon

def CreateCircle(canvas, center, radius, outline, fill, width):
	"""
	Returns shape id

	center: sympy.geometry.point.Point

	radius: number

	outline: color string (empty string for transparent)

	fill: color string (empty string for transparent)

	width: number
	"""
	radius_vect = Point(radius, radius)
	topLeft = center - radius_vect
	bottomRight = center + radius_vect
	return canvas.create_oval((topLeft.x, topLeft.y, bottomRight.x, bottomRight.y), outline = outline, fill = fill, width = width)

def CreatePolygon(canvas, pointsList, outline, fill, width):
	"""
	Returns shape id

	pointList: A list of sympy.geometry.point.Point

	outline: color string (empty string for transparent)

	fill: color string (empty string for transparent)

	width: number
	"""
	coords = []
	for p in pointsList:
		coords += [p.x, p.y]
	return canvas.create_polygon(coords, outline = outline, fill = fill, width = width)
