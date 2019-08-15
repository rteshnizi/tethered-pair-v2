from CGAL.CGAL_Kernel import cross_product as _cross_product
from CGAL.CGAL_Kernel import Line_2 as Line
from CGAL.CGAL_Kernel import Point_2 as Point
from CGAL.CGAL_Kernel import Polygon_2 as Polygon
from CGAL.CGAL_Kernel import Segment_2 as Segment
from CGAL.CGAL_Kernel import Vector_2 as Vector
from CGAL.CGAL_Kernel import Vector_3 as Vector3D
from CGAL.CGAL_Kernel import Ref_int as IntRef

from CGAL.CGAL_Triangulation_2 import Constrained_Delaunay_triangulation_2 as CgalTriangulation
from CGAL.CGAL_Triangulation_2 import Ref_Constrained_Delaunay_triangulation_2_Face_handle as TriangulationFaceRef

from CGAL.CGAL_Convex_hull_2 import convex_hull_2 as ConvexHull

def convertToPoint(vert) -> Point:
	"""
	Utility function that takes a Vertex or Point and returns a Point
	"""
	if (isinstance(vert, Point)):
		return vert
	return vert.loc

def crossProduct(vec1: Vector, vec2: Vector) -> Vector3D:
	vec1_3d = Vector3D(vec1.x(), vec1.y(), 0)
	vec2_3d = Vector3D(vec2.x(), vec2.y(), 0)
	return _cross_product(vec1_3d, vec2_3d)

# region _repr fixers

# More human readable __repr__ for Point_2
def __Pt2Repr(self):
	return "Pt2(%d, %d)" % (self.x(), self.y())
Point.__repr__ = __Pt2Repr

# More human readable __repr__ for Vector_2
def __Vec2Repr(self):
	return "Vec2(%d, %d)" % (self.x(), self.y())
Vector.__repr__ = __Vec2Repr

# More human readable __repr__ for Vector_3
def __Vec3Repr(self):
	return "Vec3(%d, %d, %d)" % (self.x(), self.y(), self.z())
Vector3D.__repr__ = __Vec3Repr

# endregion
