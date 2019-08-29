from model.modelService import Model
import utils.cgal.geometry as geometry

model = Model()

class LabeledVert(object):
	def __init__(self, vertex, robot):
		self.vrt = vertex
		self.rbt = robot

	def __repr__(self):
		return "<%s, %s>" % (self.vrt.name, self.rbt.name)

def findGaps(v, r):
	# TODO: Only look at gaps that are inside the bounding box (or partially inside)
	if v.loc == r.destination.loc:
		return [LabeledVert(r.destination, r)]
	verts = []
	for u in model.vertices:
		if not v.isVisible(u):
			continue
		# Detecting whether u is a gap for v
		epsilon = geometry.getEpsilonVector(v, u)
		if not u.ownerObs.enclosesPoint(u.loc + epsilon):
			verts.append(LabeledVert(u, r))
	return verts
