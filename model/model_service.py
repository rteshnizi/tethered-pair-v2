
class Model:
	class __PrivateModel:
		def __init__(self):
			self.MAX_CABLE = 0
			self.entities = []
			self.robots = []
			self.obstacles = []
			self.vertices = []
			self.cable = []

	instance = None

	def __init__(self):
		if not Model.instance:
			Model.instance = Model.__PrivateModel()

	def __getattr__(self, name):
		return getattr(self.instance, name)
