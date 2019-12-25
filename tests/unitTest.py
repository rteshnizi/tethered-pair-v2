from abc import ABC, abstractmethod

class UnitTest(ABC):
	def __init__(self, name, numTests):
		self.name = name
		self.numTests = numTests

	def __repr__(self):
		return "%s" % self.name

	@abstractmethod
	def run(self, verbose:bool=False):
		pass
