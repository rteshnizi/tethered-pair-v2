from utils.logger import Logger

logger = Logger()

class Model(object):
	class __PrivateModel:
		def __init__(self):
			self.MAX_CABLE = 0
			self.entities = {}
			self.robots = []
			self.obstacles = []
			self.vertices = [] # This is strictly obstacle vertices
			self.cable = [] # Initial Cable Config
			self.canvas = None # The Canvas class (not the tk.Canvas object)
			self.app = None # To read GUI attributes
			self._vertexByLocation = {} # This is all vertices including robots and destinations
			self._vertexObjects = []
			self.tempVertices = {} # This is used in partial calculation
			self._tmpACounter = 0
			self._tmpBCounter = 0
			self.solution = None

	instance = None

	def __init__(self, forceCreation=False):
		"""
		Use `forceCreation` for reseting the model.
		It should only be used carefully and between sessions.

		FIXME: Check what happens to canvas and whether the memory is cleared when this happens
		"""
		if forceCreation or not Model.instance:
			Model.instance = Model.__PrivateModel()

	def __getattr__(self, name):
		return getattr(self.instance, name)

	def setSolution(self, solution):
		self.instance.solution = solution

	def setCanvas(self, canvas):
		self.instance.canvas = canvas

	def setApp(self, app):
		self.instance.app = app

	def setMaxCable(self, l, log=False):
		self.instance.MAX_CABLE = l
		logger.log("MAX CABLE = %d" % self.instance.MAX_CABLE)

	def addVertexByLocation(self, vert):
		self.instance._vertexByLocation[ptToStringId(vert.loc)] = vert
		if vert.name.startswith("tmp-"):
			self.instance.tempVertices[vert.name] = vert

	def getVertexByLocation(self, x, y):
		return self.instance._vertexByLocation.get(xyToStringId(x, y), None)

	def removeTempVertex(self, vert):
		if not vert.name.startswith("tmp-"): return
		vert.removeShape()
		self.instance.entities.pop(vert.name, None)
		self.instance._vertexByLocation.pop(ptToStringId(vert.loc), None)
		self.instance.tempVertices.pop(vert.name, None)

	def addTempVertex(self, vert, isA):
		if not vert.name.startswith("tmp-"): return
		if isA:
			vert.name = "tmp-a-%d" % self.instance._tmpACounter
			self.instance._tmpACounter += 1
		else:
			vert.name = "tmp-b-%d" % self.instance._tmpBCounter
			self.instance._tmpBCounter += 1
		self.instance.entities[vert.name] = vert
		self.addVertexByLocation(vert)

	def removeTriangulationEdges(self):
		for key in list(self.instance.entities.keys()):
			if not key.startswith("TE-"): continue
			self.instance.entities[key].removeShape()
			self.instance.entities.pop(key)
	@property
	def allVertexObjects(self):
		"""
		This returns everything that is an instance of Vertex.
		the vertices member only holds Obstacle vertices.
		"""
		if not self.instance._vertexObjects:
			self.instance._vertexObjects = self.instance.vertices + self.instance.robots + [self.instance.robots[0].destination, self.instance.robots[1].destination]
		return self.instance._vertexObjects

def ptToStringId(pt):
	"""
	Use this method internally to obtain a unique Id for each point in this triangulation
	"""
	return xyToStringId(pt.x(), pt.y())

def xyToStringId(x, y):
	"""
	Use this method internally to obtain a unique Id for each point in this triangulation
	"""
	return '%.15f,%.15f' % (x, y)
