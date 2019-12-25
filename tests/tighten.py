import os

from algorithm.cableAlgorithms import testTightenCable
from model.preset import Preset
from tests.unitTest import UnitTest, TestResults, Verbosity

class TestTighten(UnitTest):
	def __init__(self):
		self._presetsDir = os.path.join(os.path.dirname(__file__), "..", "presets")
		# None indicates expected failed test that needs debugging
		self._tests = {
			"1.json": "[O3-2, R1, O0-0, O0-1, O3-0]",
			"10.json": "[D1, D2]",
			"11.json": "[D1, O1-1, O0-1, O0-0]",
			"12.json": "[D1, O1-1]",
			"13.json": "[O5-0, O1-0]",
			"14.json": "[O5-0, O2-2, O2-0, O3-0]",
			"15.json": "[O1-0, O2-1, O3-1]",
			"16.json": "[O5-0, O0-2, O0-0, O0-1, O2-0]",
			"17.json": "[O1-2, O0-0, O0-1, O2-1, O3-1, O5-1]",
			"18.json": "[O0-2, O0-0, O0-1, O1-1, D2]",
			"19.json": "[D1, O0-0, O0-1, O1-1, D2]",
			"2.json": "[O0-0, O0-1, O1-1]",
			"20.json": "[O1-1, O2-0, O2-2, D2]",
			"21.json": "[O2-2, R1, O2-0, O2-2, D2]",
			"22.json": "[O1-1, R1, O0-0, O0-1, O3-2]",
			"3.json": "[D1, O0-0, O0-1, D2]",
			"4.json": "[O1-2, O0-0, O0-1, O2-1, O3-1]",
			"5.json": "[O1-2, O0-0, O0-1, O2-0]",
			"6.json": "[O1-2, O0-0, O0-1, O2-1, O3-1, O5-1]",
			"7.json": "[O5-0, O0-2, O0-0, O0-1, O2-1, O3-1, O5-1]",
			"8.json": "[O5-0, O0-2, O0-0]",
			"9.json": "[O0-0, O0-1, O2-1, O3-1, O5-1]",
			"default.json": "[D1, O0-0, O0-1, O2-1, O3-1, D2]",
			"old.json": "[D1, O0-0, O0-1, D2]"
		}

		super().__init__(name="Tighten", numTests=len(self._tests))

	def run(self, verbosity=Verbosity.NONE) -> TestResults:
		results = TestResults(self.name)
		for presetName in self._tests:
			if not self._tests[presetName]:
				if verbosity > Verbosity.MEDIUM: print("Skipping %s as it is known to fail" % presetName)
				results.skipped += 1
				continue
			try:
				mapPath = os.path.join(self._presetsDir, presetName)
				mapPath = os.path.abspath(mapPath)
				preset = Preset(mapPath)
				finalCable = testTightenCable()
				finalCableStr = repr(finalCable)
				if finalCableStr == self._tests[presetName]:
					if verbosity > Verbosity.MEDIUM: print("Passed %s" % presetName)
					results.passed += 1
				else:
					results.failed += 1
					if verbosity > Verbosity.LEAST:
						print("Failed %s" % presetName)
						print("Expected\t%s" % self._tests[presetName])
						print("Received\t%s" % finalCableStr)
			except Exception as e:
				results.exception += 1
				if verbosity > Verbosity.NONE:
					print("Exception in %s" % presetName)
					print(e)
		return results
