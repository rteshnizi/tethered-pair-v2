import sys
import os
import csv
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

class CsvDataIndices(Enum):
	CABLE_LENGTH = 0
	EXPANDED = 1
	GENERATED = 2
	TIME = 3
	PATH_A_L = 4
	PATH_B_L = 5
	CABLE_L = 6
	PATH_A = 7
	PATH_B = 8
	CABLE = 9

class CsvData:
	def __init__(self, csvReader):
		self.reader = csvReader
		self.cableLength = []
		self.expanded = []
		self.generated = []
		self.time = []
		self.pathAL = []
		self.pathBL = []
		self.cableL = []
		self.pathA = []
		self.pathB = []
		self.cable = []
		self.readData()

	def readData(self):
		rowInd = -1
		for row in self.reader:
			rowInd += 1
			if rowInd == 0: continue
			self.cableLength.append(float(row[CsvDataIndices.CABLE_LENGTH.value]))
			self.expanded.append(float(row[CsvDataIndices.EXPANDED.value]))
			self.generated.append(float(row[CsvDataIndices.GENERATED.value]))
			self.time.append(float(row[CsvDataIndices.TIME.value]))
			self.pathAL.append(float(row[CsvDataIndices.PATH_A_L.value]))
			self.pathBL.append(float(row[CsvDataIndices.PATH_B_L.value]))
			self.cableL.append(float(row[CsvDataIndices.CABLE_L.value]))
			self.pathA.append(row[CsvDataIndices.PATH_A.value])
			self.pathB.append(row[CsvDataIndices.PATH_B.value])
			self.cable.append(row[CsvDataIndices.CABLE_LENGTH.value])

def main(path):
	# plt.style.use('ggplot')
	csvPath = os.path.abspath(path)
	with open(csvPath, "r", newline="") as csvFile:
		csvReader = csv.reader(csvFile, quoting=csv.QUOTE_ALL)
		csvData = CsvData(csvReader)
		(fig, ax) = plt.subplots()
		R = np.linspace(0.7, 1, 3)
		cmap = plt.cm.get_cmap("Blues", 256)
		colors = cmap(R)
		ax.stackplot(csvData.cableLength, csvData.expanded, np.subtract(csvData.generated, csvData.expanded), colors=colors)
		plt.show()

if __name__ == '__main__':
	main(sys.argv[1])
