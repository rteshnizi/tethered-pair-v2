from tests.tighten import TestTighten

def main():
	unitTests = { TestTighten() }
	for test in unitTests:
		print("Running %s: %d test cases" % (test.name, test.numTests))
		result = test.run()
		print(result)

if __name__ == '__main__':
	main()
