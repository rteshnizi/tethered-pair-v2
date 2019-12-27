import os

from algorithm.cable import testTightenCable
from model.preset import Preset
from tests.unitTest import UnitTest, TestResults, Verbosity

class TestTighten(UnitTest):
	def __init__(self):
		self._presetsDir = os.path.join(os.path.dirname(__file__), "..", "presets")
		# None indicates expected failed test that needs debugging
		super().__init__(name="Tighten", tests={
			"default.json": "[D1, O0-0, O0-1, O1-1, O1-2, D2]",
			"1.json": "[O1-3, R1, O0-0, O0-1, O1-1]",
			"2.json": "[O0-0, O0-1, O0-2]",
			"3.json": "[D1, O0-0, O0-1, D2]",
			"4.json": "[O0-3, O0-0, O0-1, O1-1, O1-2]",
			"5.json": "[O0-3, O0-0, O0-1, O1-0]",
			"6.json": "[O0-3, O0-0, O0-1, O1-1, O1-2, O2-2]",
			"7.json": "[O2-1, O0-3, O0-0, O0-1, O1-1, O1-2, O2-2]",
			"8.json": "[O2-1, O0-3, O0-0]",
			"9.json": "[O0-0, O0-1, O1-1, O1-2, O2-2]",
			"10.json": "[D1, D2]",
			"11.json": "[D1, O0-2, O0-1, O0-0]",
			"12.json": "[D1, O0-2]",
			"13.json": "[O2-1, O0-1]",
			"14.json": "[O2-1, O1-3, O1-0, O1-1]",
			"15.json": "[O0-1, O1-1, O1-2]",
			"16.json": "[O2-1, O0-3, O0-0, O0-1, O1-0]",
			"17.json": "[O0-3, O0-0, O0-1, O1-1, O1-2, O2-2]",
			"18.json": "[O0-2, O0-0, O0-1, O1-1, D2]",
			"19.json": "[D1, O0-0, O0-1, O1-1, D2]",
			"20.json": "[O1-1, O2-0, O2-2, D2]",
			"21.json": "[O2-2, R1, O2-0, O2-2, D2]",
			"22.json": "[O0-2, R1, O0-0, O0-1, O1-3]",
			"23.json": "[D1, O1-0, O1-1, O1-2, O2-0, O2-3, D2]",
		})

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
				finalCable = testTightenCable()
				finalCableStr = repr(finalCable)
				if finalCableStr == self._tests[presetName]:
					if verbosity > Verbosity.MEDIUM: self._reportSuccessfulTest(presetName)
					results.passed += 1
				else:
					results.failed += 1
					if verbosity > Verbosity.LEAST:
						self._reportFailedTest(presetName, finalCableStr)
			except Exception as e:
				results.exception += 1
				if verbosity > Verbosity.NONE:
					self._reportException(presetName, e)
		return results
