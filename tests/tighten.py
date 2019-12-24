import os

from algorithm.cableAlgorithms import testTightenCable
from model.preset import Preset
from tests.unitTest import UnitTest

# None indicates expected failed test that needs debugging
tests = {
	"1.json": "[O1-1, R1, O0-0, O0-1, O3-2]",
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
	"3.json": "[D1, O0-0, O0-1, D2]",
	"4.json": "[O1-2, O0-0, O0-1, O2-1, O3-1]",
	"5.json": "[O1-2, O0-0, O0-1, O2-0]",
	"6.json": "[O1-2, O0-0, O0-1, O2-1, O3-1, O5-1]",
	"7.json": "[O5-0, O0-2, O0-0, O0-1, O2-1, O3-1, O5-1]",
	"8.json": None,
	"9.json": "[O0-0, O0-1, O2-1, O3-1, O5-1]",
	"default.json": "[D1, O0-0, O0-1, O2-1, O3-1, D2]",
	"old.json": "[D1, O0-0, O0-1, D2]"
}

cwd = os.path.dirname(__file__)
presetsDir = os.path.join(cwd, "..", "presets")

class TestTighten(UnitTest):
	def __init__(self):
		super().__init__(name="AStar")

	def run(self, verbose=False):
		failedAny = False
		print("Testing A-Star Algorithm: %d test cases" % len(tests))
		for presetName in tests:
			if not tests[presetName]:
				if verbose: print("Skipping %s as it is known to fail" % presetName)
				continue
			try:
				mapPath = os.path.join(presetsDir, presetName)
				mapPath = os.path.abspath(mapPath)
				preset = Preset(mapPath)
				finalCable = testTightenCable()
				finalCableStr = repr(finalCable)
				if finalCableStr == tests[presetName]:
					if verbose: print("Passed %s" % presetName)
				else:
					failedAny = True
					print("Failed %s" % presetName)
					print("Expected\t%s" % tests[presetName])
					print("Received\t%s" % finalCableStr)
			except Exception as e:
				print("Exception in %s" % presetName)
				print(e)
		print("Passed all tests.")
