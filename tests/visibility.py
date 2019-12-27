import os

from model.preset import Preset
from tests.unitTest import UnitTest, TestResults, Verbosity

class TestVisibility(UnitTest):
	def __init__(self):
		self._presetsDir = os.path.join(os.path.dirname(__file__), "..", "presets")
		super().__init__(name="Visibility", tests={
			"default.json": 186,
			"20.json": 179,
			"22.json": 198,
		})

	def _countEdges(self, preset: Preset):
		counter = 0
		for v in preset.model.allVertexObjects:
			for u in v.gaps:
				counter += 1
		return counter

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
				count = self._countEdges(preset)
				if count == self._tests[presetName]:
					if verbosity > Verbosity.MEDIUM: self._reportSuccessfulTest(presetName)
					results.passed += 1
				else:
					results.failed += 1
					if verbosity > Verbosity.LEAST:
						self._reportFailedTest(presetName, count)
			except Exception as e:
				results.exception += 1
				if verbosity > Verbosity.NONE:
					self._reportException(presetName, e)
		return results
