import os
import csv
from statistics import mean
from algorithm.aStar import aStar
from algorithm.solutionLog import SolutionLog
from model.preset import Preset
import utils.cgal.geometry as Geom
from utils.logger import Logger

logger = Logger()

csvData = [["CABLE-LENGTH", "EXPANDED", "GENERATED", "TIME", "PATH-A-L", "PATH-B-L", "CABLE-L", "PATH-A", "PATH-B", "CABLE"]]

def main():
	presetsPath = os.path.join(os.path.dirname(__file__), "presets", "scenario-1.json")
	for MAX_CABLE in range(200, 701, 2):
		try:
			mapPath = os.path.abspath(presetsPath)
			preset = Preset(mapPath)
			preset.model.setMaxCable(MAX_CABLE)
			# times = []
			# for i in range(3):
			# 	logger.log("Iter %d" % i)
			# 	solution = aStar()
			# 	times.append(solution.time)
			# solution.time = mean(times)
			solution = aStar()
			logSolution(solution)
			logger.log("Elapsed time = %f" % solution.time)
		except Exception as e:
			logger.log(e)
	with open(logger.logFileName.replace(".log", ".csv"), "w", newline="") as csvFile:
		csvWriter = csv.writer(csvFile, quoting=csv.QUOTE_ALL)
		for row in csvData:
			csvWriter.writerow(row)

def logSolution(solution: SolutionLog):
	if not solution:
		logger.log("NO SOLUTIONS")
		return
	pathA = solution.content.paths[0]
	pathB = solution.content.paths[1]
	pathAL = Geom.lengthOfCurve(pathA)
	pathBL = Geom.lengthOfCurve(pathB)
	cable = solution.content.cable
	cableL = Geom.lengthOfCurve(cable)
	# ["CABLE LENGTH", "EXPANDED", "GENERATED", "TIME", "PATH-A-L", "PATH-B-L", "CABLE-L", "PATH-A", "PATH-B", "CABLE"]
	csvRow = [solution.maxCable, solution.expanded, solution.genereted, solution.time, pathAL, pathBL, cableL, pathA, pathB, cable]
	csvData.append(csvRow)
	logger.log("PATHS: %s - L = [%.2f, %.2f]" % (repr(solution.content.paths), pathAL, pathBL))
	logger.log("CABLE-D: %s - L = %.2f" % (repr(cable), cableL))

if __name__ == '__main__':
	main()
