import utils.cgal.geometry as Geom
from math import fabs, nan, isnan
from utils.vertexUtils import convertToPoint, getClosestVertex, almostEqual, removeRepeatedVertsOrdered
from algorithm.node import Node
from algorithm.cable import tightenCable, getLongCable
from model.modelService import Model
from model.vertex import Vertex
from utils.priorityQ import PriorityQ
from utils.cgal.types import Polygon

model = Model()

def aStar(debug=False) -> Node:
	pass
