class Model:
	class __PrivateModel:
		def __init__(self):
			self.MAX_CABLE = 0
			self.entities = {}
			self.robots = []
			self.obstacles = []
			self.vertices = [] # This is strictly obstacle vertices
			self.cable = [] # Initial Cable Config
			self.visualElements = [] # Holds only visualization elements
			self._vertexByLocation = {} # This is all vertices including robots and destinations
			self.canvas = None # The Canvas class (not the tk.Canvas object)
			self.app = None # To read GUI attributes

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

	def setCanvas(self, canvas):
		self.instance.canvas = canvas

	def setApp(self, app):
		self.instance.app = app

	def setMaxCable(self, l):
		self.instance.MAX_CABLE = l

	def addVertexByLocation(self, vert):
		self._vertexByLocation[ptToStringId(vert.loc)] = vert

	def getVertexByLocation(self, x, y):
		return self._vertexByLocation.get(xyToStringId(x, y), None)

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
