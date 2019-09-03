from model.entity import Entity
from model.modelService import Model
from model.vertex import Vertex
from utils.cgal.drawing import CreatePolygon
import utils.cgal.geometry as Geom
from utils.cgal.types import Point
import utils.vertexUtils as VertexUtils

CABLE_ORIGIN_COLOR = "Green"
CABLE_FINAL_COLOR = "Orange"
model = Model()

class Cable(Entity):
	def __init__(self, canvas, name, pts: list, isOrigin=False):
		"""
		params
		===

		canvas: tk.Canvas

		color: color string

		name: str

		pts: A list of at least 2 utils.cgal.types.Point
		"""
		super().__init__(canvas=canvas, color=CABLE_ORIGIN_COLOR if isOrigin else CABLE_FINAL_COLOR, name=name)
		if isinstance(pts, list):
			if len(pts) < 2:
				raise RuntimeError("at least 2 Points are needed for a Cable")
		# for cable we draw a polygon just so we have a single id instead of a group of IDs for line segments
		self.pts = [VertexUtils.convertToPoint(v) for v in pts]
		for v in reversed(pts):
			pt = VertexUtils.convertToPoint(v)
			self.pts.append(Geom.addVectorToPoint(pt, 2, 2))
		self.createShape()

	def createShape(self):
		if (self.canvasId): return
		self.canvasId = CreatePolygon(self.canvas, pointsList=self.pts, outline="", fill=self.color, width=5, tag=self.name)
