import os
import csv
from statistics import mean
from algorithm.aStar import aStar
from algorithm.solutionLog import SolutionLog
from model.preset import Preset
import utils.cgal.geometry as Geom
from utils.logger import Logger

logger = Logger()

csvData = [["HEURISTIC", "EXPANDED", "GENERATED", "TIME"]]

def main():
	presetsPath = os.path.join(os.path.dirname(__file__), "presets", "scenario-1.json")
	heuristics = ["_heuristicNone", "_heuristicLineDist", "_heuristicShortestPath", "_heuristicTrmpp"]
	for heuristic in heuristics:
		try:
			mapPath = os.path.abspath(presetsPath)
			preset = Preset(mapPath)
			solution = aStar(heuristic)
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
	# ["HEURISTIC", "EXPANDED", "GENERATED", "TIME"]
	csvRow = [solution.heuristic, solution.expanded, solution.genereted, solution.time]
	csvData.append(csvRow)
	logger.log("PATHS: %s - L = [%.2f, %.2f]" % (repr(solution.content.paths), pathAL, pathBL))
	logger.log("CABLE-D: %s - L = %.2f" % (repr(cable), cableL))

if __name__ == '__main__':
	main()
