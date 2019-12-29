import os

from model.preset import Preset
from algorithm.aStar import aStar
from tests.unitTest import UnitTest, TestResults, Verbosity

class TestAStar(UnitTest):
	def __init__(self):
		self._presetsDir = os.path.join(os.path.dirname(__file__), "..", "presets")
		super().__init__(name="aStar", tests={
			"10.json": ["[R1, D1]", "[R2, D2]"],
		})

	def _isCorrectSolution(self, paths: list, presetName: str):
		return repr(paths[0]) == self._tests[presetName][0] and repr(paths[1]) == self._tests[presetName][1]

	def run(self, verbosity=Verbosity.NONE) -> TestResults:
		results = TestResults(self.name)
		for presetName in self._tests:
			if not self._tests[presetName]:
				if verbosity > Verbosity.MEDIUM: self._reportSkippedTest(presetName)
				results.skipped += 1
				continue
			try:
				mapPath = os.path.join(self._presetsDir, presetName)
				mapPath = os.path.abspath(mapPath)
				preset = Preset(mapPath)
				solution = aStar()
				paths = solution.getPaths()
				if self._isCorrectSolution(paths, presetName):
					if verbosity > Verbosity.MEDIUM: self._reportSuccessfulTest(presetName)
					results.passed += 1
				else:
					results.failed += 1
					if verbosity > Verbosity.LEAST:
						self._reportFailedTest(presetName, paths)
			except Exception as e:
				results.exception += 1
				if verbosity > Verbosity.NONE:
					self._reportException(presetName, e)
		return results
