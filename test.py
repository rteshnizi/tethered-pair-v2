import sys

from tests.visibility import TestVisibility
from tests.tighten import TestTighten
from tests.aStar import TestAStar
from tests.unitTest import Verbosity

def main(verbosity=Verbosity.NONE):
	unitTests = [TestVisibility(), TestTighten(), TestAStar()]
	for test in unitTests:
		print("Running %s: %d test cases" % (test.name, test.numTests))
		result = test.run(verbosity)
		print(result)
		print()

if __name__ == '__main__':
	verbosity = Verbosity.NONE
	if "-v1" in sys.argv: verbosity = Verbosity.LEAST
	elif "-v2" in sys.argv: verbosity = Verbosity.MEDIUM
	elif "-v3" in sys.argv: verbosity = Verbosity.MOST
	print("Verbosity = %s" % str(verbosity)[10:])
	print()
	main(verbosity)
