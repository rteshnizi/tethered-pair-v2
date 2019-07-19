from model.model_service import Model
import utils.cgal.geometry as geometry

model = Model()

class Gap(object):
	def __init__(self, vertex, robot):
		self.vrt = vertex
		self.rbt = robot

	def __repr__(self):
		return "<%s, %s>" % (self.vrt.name, self.rbt.name)

def gapDetector(v, r):
	# TODO: Only look at gaps that are inside the bounding box (or partially inside)
	if v.loc.equals(r.destination.loc):
		return [Gap(r.destination, r)]
	gaps = []
	for u in model.vertices:
		# Detecting whether u is a gap for v
		epsilon = geometry.getEpsilonVector(v, u)
		if (not u.ownerObs.polygon.encloses_point(u.loc + epsilon)):
			gaps.append(Gap(u, r))
	return gaps
