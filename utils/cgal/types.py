from CGAL.CGAL_Kernel import cross_product as crossProduct
from CGAL.CGAL_Kernel import Line_2 as Line
from CGAL.CGAL_Kernel import Point_2 as Point
from CGAL.CGAL_Kernel import Polygon_2 as Polygon
from CGAL.CGAL_Kernel import Segment_2 as Segment
from CGAL.CGAL_Kernel import Vector_2 as Vector
from CGAL.CGAL_Kernel import Ref_int as IntRef

from CGAL.CGAL_Triangulation_2 import Constrained_Delaunay_triangulation_2 as CgalTriangulation
from CGAL.CGAL_Triangulation_2 import Ref_Constrained_Delaunay_triangulation_2_Face_handle as TriangulationFaceRef

from CGAL.CGAL_Convex_hull_2 import convex_hull_2 as ConvexHull

# More human readable __repr__ for Point_2
def __fixedRepr(self):
	return "CgalPt(%d, %d)" % (self.x(), self.y())

Point.__repr__ = __fixedRepr

def convertToPoint(vert) -> Point:
	"""
	Utility function that takes a Vertex or Point and returns a Point
	"""
	return vert.loc if vert.loc else vert
