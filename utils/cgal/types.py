from CGAL.CGAL_Kernel import Point_2 as Point
from CGAL.CGAL_Kernel import Polygon_2 as Polygon
from CGAL.CGAL_Kernel import Segment_2 as Segment
from CGAL.CGAL_Kernel import Vector_2 as Vector
from CGAL.CGAL_Triangulation_2 import Constrained_triangulation_2 as CgalTriangulation
from CGAL.CGAL_Convex_hull_2 import convex_hull_2 as ConvexHull

def __fixedRepr(self):
	return "CgalPt(%d, %d)" % (self.x(), self.y())


Point.__repr__ = __fixedRepr
