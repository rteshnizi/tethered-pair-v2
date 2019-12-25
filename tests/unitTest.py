from abc import ABC, abstractmethod
from enum import IntEnum

class Verbosity(IntEnum):
	NONE = 0
	LEAST = 1
	MEDIUM = 2
	MOST = 3

class TestResults(object):
	def __init__(self, name):
		self.name = name
		self.passed = 0
		self.failed = 0
		self.skipped = 0
		self.exception = 0

	def __repr__(self):
		return "%s Results: %d passed, %d failed, %d skipped, %d threw Exception" % (self.name, self.passed, self.failed, self.skipped, self.exception)

class UnitTest(ABC):
	def __init__(self, name, numTests):
		self.name = name
		self.numTests = numTests

	def __repr__(self):
		return "%s" % self.name

	@abstractmethod
	def run(self, verbosity:Verbosity=Verbosity.NONE) -> TestResults:
		pass
