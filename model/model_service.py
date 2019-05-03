
class Model:
	class __PrivateModel:
		def __init__(self):
			self.MAX_CABLE = 0
			self.entities = {}
			self.robots = []
			self.obstacles = []
			self.vertices = [] # This is strictly obstacle vertices
			self.cable = []
			self._vertexByLocation = {} # This is all vertices including robots and destinations

		def addVertexByLocation(self, vert):
			self._vertexByLocation['%d,%d' % (vert.loc.x, vert.loc.y)] = vert

		def getVertexByLocation(self, vert):
			return self._vertexByLocation.get('%d,%d' % (vert.loc.x, vert.loc.y), None)

	instance = None

	def __init__(self):
		if not Model.instance:
			Model.instance = Model.__PrivateModel()

	def __getattr__(self, name):
		return getattr(self.instance, name)
