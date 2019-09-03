from model.modelService import Model
from model.robot import Robot
import utils.cgal.geometry as geometry

model = Model()

class LabeledVert(object):
	def __init__(self, vertex, robot):
		self.vrt = vertex
		self.rbt = robot

	def __repr__(self):
		return "<%s, %s>" % (self.vrt.name, self.rbt.name)

def findGaps(v, r: Robot):
	# TODO: Only look at gaps that are inside the bounding box (or partially inside)
	if v.loc == r.destination.loc:
		return [LabeledVert(r.destination, r)]
	verts = []
	if _isGap(v, r.destination):
		verts.append(LabeledVert(r.destination, r))
	for u in model.vertices:
		if _isGap(v, u):
			verts.append(LabeledVert(u, r))
	return verts

def _isGap(src, target) -> bool:
	if not src.isVisible(target):
		return False
	# Detecting whether u is a gap for v
	epsilon = geometry.getEpsilonVector(src, target)
	if target.ownerObs and target.ownerObs.enclosesPoint(target.loc + epsilon):
		return False
	return True
