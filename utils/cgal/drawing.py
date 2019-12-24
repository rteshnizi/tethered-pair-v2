from model.modelService import Model
from utils.cgal.types import Point, Vector

model = Model()

def CreateCircle(canvas, center, radius, outline, fill, width, tag):
	"""
	Returns shape id

	center: utils.cgal.types.Point

	radius: number

	outline: color string (empty string for transparent)

	fill: color string (empty string for transparent)

	width: number

	tag: a unique identifier (use entity name)
	"""
	radius_vect = Vector(radius, radius)
	topLeft = center - radius_vect
	bottomRight = center + radius_vect
	shape = canvas.create_oval((topLeft.x(), topLeft.y(), bottomRight.x(), bottomRight.y()), outline=outline, fill=fill, width=width, tag=tag)
	bindMouseEvent(canvas, shape)
	return shape

def CreatePolygon(canvas, pointsList, outline, fill, width, tag):
	"""
	Returns shape id

	pointList: A list of utils.cgal.types.Point

	outline: color string (empty string for transparent)

	fill: color string (empty string for transparent)

	width: number

	tag: a unique identifier (use entity name)
	"""
	coords = []
	for p in pointsList:
		coords += [p.x(), p.y()]
	shape = canvas.create_polygon(coords, outline=outline, fill=fill, width=width, tag=tag)
	bindMouseEvent(canvas, shape)
	return shape

def CreateLine(canvas, pointsList, color, tag, width=1, dash=()):
	"""
	Returns shape id

	pointList: A list of utils.cgal.types.Point

	color: color string (empty string for transparent)

	width: number; default is 1

	dash: Dash pattern, given as a list of segment lengths. Only the odd segments are drawn.

	tag: a unique identifier (use entity name)
	"""
	coords = []
	for p in pointsList:
		coords += [p.x(), p.y()]
	shape = canvas.create_line(coords, fill=color, width=width, dash=dash, tag=tag)
	bindMouseEvent(canvas, shape)
	return shape

def bindMouseEvent(canvas, shape):
	canvas.tag_bind(shape, '<Enter>', mouseHandler)

def mouseHandler(event):
	if not model.app.shouldPrintMouse: return
	shape = event.widget.find_closest(event.x, event.y)
	tag = model.canvas.gettags(shape)[0]
	entity = model.entities.get(tag)
	if not entity: return
	if hasattr(entity, 'loc'):
		print('%s-%d,%d' % (tag, entity.loc.x(), entity.loc.y()))
	else:
		print(tag)

def RemoveShape(canvas, shapeId):
	"""
	Remove a shape from canvas
	"""
	canvas.delete(shapeId)
