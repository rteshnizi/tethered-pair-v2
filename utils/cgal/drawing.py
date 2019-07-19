from utils.cgal.types import Point, Vector

def CreateCircle(canvas, center, radius, outline, fill, width):
	"""
	Returns shape id

	center: utils.cgal.types.Point

	radius: number

	outline: color string (empty string for transparent)

	fill: color string (empty string for transparent)

	width: number
	"""
	radius_vect = Vector(radius, radius)
	topLeft = center - radius_vect
	bottomRight = center + radius_vect
	return canvas.create_oval((topLeft.x(), topLeft.y(), bottomRight.x(), bottomRight.y()), outline=outline, fill=fill, width=width)

def CreatePolygon(canvas, pointsList, outline, fill, width):
	"""
	Returns shape id

	pointList: A list of utils.cgal.types.Point

	outline: color string (empty string for transparent)

	fill: color string (empty string for transparent)

	width: number
	"""
	coords = []
	for p in pointsList:
		coords += [p.x(), p.y()]
	return canvas.create_polygon(coords, outline=outline, fill=fill, width=width)

def CreateLine(canvas, pointsList, color, width=1, dash=()):
	"""
	Returns shape id

	pointList: A list of utils.cgal.types.Point

	color: color string (empty string for transparent)

	width: number; default is 1

	dash: Dash pattern, given as a list of segment lengths. Only the odd segments are drawn.
	"""
	coords = []
	for p in pointsList:
		coords += [p.x(), p.y()]
	return canvas.create_line(coords, fill=color, width=width, dash=dash)

def RemoveShape(canvas, shapeId):
	"""
	Remove a shape from canvas
	"""
	canvas.delete(shapeId)
