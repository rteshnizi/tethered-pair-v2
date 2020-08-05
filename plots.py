import sys
import os
import csv
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

# https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html#colorcet
cMapC = plt.cm.get_cmap("tab20c", 256)
purples = cMapC([0.69, 0.61])
cMap0 = plt.cm.get_cmap("tab20", 256)
blues = cMap0([0.09, 0.01])
lightBlues = cMap0([0.99, 0.91])
cMapB = plt.cm.get_cmap("tab20b", 256)
reds = cMapB([0.74, 0.61])
greens = cMapB([0.39, 0.21])
pinks = cMapB([0.99, 0.81])
cMapYlBr = plt.cm.get_cmap("YlOrBr", 256)
yellows = cMapYlBr([0.2, 0.4])

class CsvDataIndices(Enum):
	LABEL = 0
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
		self.label = []
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
			label = row[CsvDataIndices.LABEL.value]
			try:
				label = float(label)
			except:
				label = row[CsvDataIndices.LABEL.value]
			self.label.append(label)
			self.expanded.append(float(row[CsvDataIndices.EXPANDED.value]))
			self.generated.append(float(row[CsvDataIndices.GENERATED.value]))
			self.time.append(float(row[CsvDataIndices.TIME.value]))
			self.pathAL.append(float(row[CsvDataIndices.PATH_A_L.value]))
			self.pathBL.append(float(row[CsvDataIndices.PATH_B_L.value]))
			self.cableL.append(float(row[CsvDataIndices.CABLE_L.value]))
			self.pathA.append(row[CsvDataIndices.PATH_A.value])
			self.pathB.append(row[CsvDataIndices.PATH_B.value])
			self.cable.append(row[CsvDataIndices.CABLE.value])

def main():
	plotLengthVsSpace()
	plotHeuristic1()
	plotHeuristic2()
	plotPaths()
	plotDp()
	plotCable()
	plt.show()

def plotDp():
	csvPath = os.path.abspath(os.path.join("logs", "dp.csv"))
	with open(csvPath, "r", newline="") as csvFile:
		csvReader = csv.reader(csvFile, quoting=csv.QUOTE_ALL)
		csvData = CsvData(csvReader)
		(fig, ax) = plt.subplots()
		# ax.set_title("Comparison of Heuristics")
		expandedColors = [0, blues[0], purples[0], 0]
		generatedColors = [0, blues[1], purples[1], 0]
		width = 0.15
		labels = ["Expanded", "Generated"]
		x = [0, 0.2, 0.55, 0.75]
		bars = []
		expanded = [0] + csvData.expanded + [0]
		bars.append(ax.bar(x, expanded, width, label=labels[0]))
		values = list(np.subtract(csvData.generated, csvData.expanded))
		bars.append(ax.bar(x, [0] + values + [0], width, bottom=expanded, label=labels[1]))
		ax.set_xticks(x[1:3])
		ax.set_xticklabels(("DP", "A*"))
		# ax.legend(loc="upper right")
		ax.set_ylabel("Nodes")
		ax.margins(0, 0.07)
		# insert plot values for expanded
		i = -1
		for rect in bars[0]:
			i += 1
			if rect.get_height() == 0: continue
			rect.set_color(expandedColors[i])
			ax.text(rect.get_x() + rect.get_width() / 2.,
					rect.get_y() + rect.get_height() + 3,
					'%d' % rect.get_height(),
					ha = 'center',
					va = 'center')
		# insert plot values for generated
		i = -1
		for rect in bars[1]:
			i += 1
			if rect.get_height() == 0: continue
			rect.set_color(generatedColors[i])
			ax.text(rect.get_x() + rect.get_width() / 2.,
					rect.get_y() + rect.get_height() + 3,
					'%d' % (rect.get_height() + expanded[i]),
					ha = 'center',
					va = 'center')


def plotHeuristic1():
	csvPath = os.path.abspath(os.path.join("logs", "heuristics.csv"))
	with open(csvPath, "r", newline="") as csvFile:
		csvReader = csv.reader(csvFile, quoting=csv.QUOTE_ALL)
		csvData = CsvData(csvReader)
		(fig, ax) = plt.subplots()
		# ax.set_title("Comparison of Heuristics")
		expandedColors = [0, blues[0], lightBlues[0], 0]
		generatedColors = [0, blues[1], lightBlues[1], 0]
		width = 0.15
		labels = ["Expanded", "Generated"]
		x = [0, 0.2, 0.55, 0.75]
		bars = []
		expanded = [0] + csvData.expanded[0:2] + [0]
		bars.append(ax.bar(x, expanded, width, label=labels[0]))
		values = list(np.subtract(csvData.generated[0:2], csvData.expanded[0:2]))
		bars.append(ax.bar(x, [0] + values + [0], width, bottom=expanded, label=labels[1]))
		ax.set_xticks(x[1:3])
		ax.set_xticklabels(("UC", "SLD"))
		# ax.legend(loc="upper right")
		ax.set_ylabel("Nodes")
		ax.margins(0, 0.07)
		# insert plot values for expanded
		i = -1
		for rect in bars[0]:
			i += 1
			if rect.get_height() == 0: continue
			rect.set_color(expandedColors[i])
			ax.text(rect.get_x() + rect.get_width() / 2.,
					rect.get_y() + rect.get_height() + 50,
					'%d' % rect.get_height(),
					ha = 'center',
					va = 'center')
		# insert plot values for generated
		i = -1
		for rect in bars[1]:
			i += 1
			if rect.get_height() == 0: continue
			rect.set_color(generatedColors[i])
			ax.text(rect.get_x() + rect.get_width() / 2.,
					rect.get_y() + rect.get_height() + 50,
					'%d' % (rect.get_height() + expanded[i]),
					ha = 'center',
					va = 'center')

def plotHeuristic2():
	csvPath = os.path.abspath(os.path.join("logs", "heuristics.csv"))
	with open(csvPath, "r", newline="") as csvFile:
		csvReader = csv.reader(csvFile, quoting=csv.QUOTE_ALL)
		csvData = CsvData(csvReader)
		(fig, ax) = plt.subplots()
		# ax.set_title("Comparison of Heuristics")
		expandedColors = [0, lightBlues[0], purples[0], pinks[0], 0]
		generatedColors = [0, lightBlues[1], purples[1], pinks[1], 0]
		width = 0.2
		labels = ["Expanded", "Generated"]
		x = [0, 0.2, 0.55, 0.9, 1]
		bars = []
		expanded = [0] + csvData.expanded[1:4] + [0]
		bars.append(ax.bar(x, expanded, width, label=labels[0]))
		values = list(np.subtract(csvData.generated[1:4], csvData.expanded[1:4]))
		bars.append(ax.bar(x, [0] + values + [0], width, bottom=expanded, label=labels[1]))
		ax.set_xticks(x[1:4])
		ax.set_xticklabels(("SLD", "SPD", "TRMPP"))
		# ax.legend(loc="upper right")
		ax.set_ylabel("Nodes")
		ax.margins(0, 0.07)
		# insert plot values for expanded
		i = -1
		for rect in bars[0]:
			i += 1
			if rect.get_height() == 0: continue
			rect.set_color(expandedColors[i])
			ax.text(rect.get_x() + rect.get_width() / 2.,
					rect.get_y() + rect.get_height() + 10,
					'%d' % rect.get_height(),
					ha = 'center',
					va = 'center')
		# insert plot values for generated
		i = -1
		for rect in bars[1]:
			i += 1
			if rect.get_height() == 0: continue
			rect.set_color(generatedColors[i])
			ax.text(rect.get_x() + rect.get_width() / 2.,
					rect.get_y() + rect.get_height() + 10,
					'%d' % (rect.get_height() + expanded[i]),
					ha = 'center',
					va = 'center')

def plotLengthVsSpace():
	csvPath = os.path.abspath(os.path.join("logs", "2020-08-03-00-39-37.csv"))
	with open(csvPath, "r", newline="") as csvFile:
		csvReader = csv.reader(csvFile, quoting=csv.QUOTE_ALL)
		csvData = CsvData(csvReader)
		(fig, ax) = plt.subplots()
		# ax.set_title("Generated vs. Expanded Nodes")
		labels = ["Expanded", "Generated"]
		ax.stackplot(csvData.label, csvData.expanded, np.subtract(csvData.generated, csvData.expanded), colors=blues, labels=labels)
		ax.legend(loc="upper right")
		ax.set_ylabel("Nodes")
		ax.set_xlabel("Max Cable Length")
		ax.margins(0, 0.07)

def plotPaths():
	csvPath = os.path.abspath(os.path.join("logs", "2020-08-03-00-39-37.csv"))
	with open(csvPath, "r", newline="") as csvFile:
		csvReader = csv.reader(csvFile, quoting=csv.QUOTE_ALL)
		csvData = CsvData(csvReader)
		(fig, ax1) = plt.subplots()
		ax1.plot(csvData.label, np.maximum(csvData.pathAL, csvData.pathBL), color=yellows[1], linewidth=5, alpha=0.5, label="Active Constraint")
		ax1.plot(csvData.label, csvData.pathAL, color=reds[0], label="Robot A")
		ax1.plot(csvData.label, csvData.pathBL, color=blues[1], label="Robot B")
		ax1.legend(loc="upper right")
		ax1.set_ylabel("Distance")
		ax1.set_xlabel("Max Cable Length")
		ax1.margins(0, 0.07)

def plotCable():
	csvPath = os.path.abspath(os.path.join("logs", "2020-08-03-00-39-37.csv"))
	with open(csvPath, "r", newline="") as csvFile:
		csvReader = csv.reader(csvFile, quoting=csv.QUOTE_ALL)
		csvData = CsvData(csvReader)
		(fig, ax1) = plt.subplots()
		ax1.plot(csvData.label, csvData.cableL, color=blues[1], label="Consumed Cable")
		ax1.plot(csvData.label, csvData.label, color=reds[0], linestyle="dashed", label="Max Cable")
		ax1.legend(loc="upper left")
		ax1.set_ylabel("Distance")
		ax1.set_xlabel("Max Cable Length")
		ax1.margins(0, 0.07)


if __name__ == '__main__':
	main()
