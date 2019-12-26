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
	"""
	tests: dictionary of testName to test result. None as value in dictionary, indicates the test should be skipped.
	"""
	def __init__(self, name, tests: dict):
		self.name = name
		self._tests: dict = tests

	@property
	def numTests(self):
		return len(self._tests)

	def __repr__(self):
		return "%s" % self.name

	def _reportSkippedTest(self, testName):
		print("Skipping %s as it is known to fail" % testName)

	def _reportSuccessfulTest(self, testName):
		print("Passed %s" % testName)

	def _reportFailedTest(self, testName, received):
		print("Failed %s" % testName)
		print("Expected\t%s" % self._tests[testName])
		print("Received\t%s" % received)

	def _reportException(self, testName, exception):
		print("Exception in %s" % testName)
		print(exception)

	@abstractmethod
	def run(self, verbosity:Verbosity=Verbosity.NONE) -> TestResults:
		pass
