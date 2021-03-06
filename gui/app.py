import os
import tkinter as tk
from tkinter import filedialog

from gui.canvas import Canvas
from algorithm.aStar import aStar
from algorithm.dp import dynamicProg
from algorithm.cable import testTightenCable, pushCableAwayFromObstacles, preprocessTheCable
from algorithm.triangulation import testTriangulation
from algorithm.visibility import processReducedVisibilityGraph

class TetheredPairApp(tk.Frame):
	def __init__(self):
		self._presetsDir = os.path.join(os.path.dirname(__file__), "..", "presets")
		self.master = tk.Tk()
		self.master.title("Tethered Pair Simulation")
		self.master.geometry("1100x850")
		super().__init__(self.master)
		self.pack()
		self.chosenPreset = tk.StringVar(master=self.master)
		self.chosenHeuristic = tk.StringVar(master=self.master)
		self._dbg = {
			# 'Print Mouse': tk.IntVar(master=self.master, value=0),
			'Test Vis Graph': tk.IntVar(master=self.master, value=0),
			'Test Triangulation': tk.IntVar(master=self.master, value=0),
			'Test Tighten Alg': tk.IntVar(master=self.master, value=0),
			'Debug Flag': tk.IntVar(master=self.master, value=0)
		}
		self.createDropdown()
		self.createButtons()
		self.createDebugOptions()
		self.canvas = Canvas(self.master, self)

	@property
	def debugFlag(self) -> bool:
		return self._dbg['Debug Flag'].get() == 1

	@property
	def shouldPrintMouse(self) -> bool:
		return False
		# return self._dbg['Print Mouse'].get() == 1

	@property
	def shouldDebugTriangulation(self) -> bool:
		return self._dbg['Test Triangulation'].get() == 1

	@property
	def shouldDebugTighten(self) -> bool:
		return self._dbg['Test Tighten Alg'].get() == 1

	@property
	def shouldDebugVisGraph(self) -> bool:
		return self._dbg['Test Vis Graph'].get() == 1

	def _getJsonPresets(self):
		isJson = lambda f: f.lower().endswith(".json")
		isNumbered = lambda f: f[:-5].isdigit()
		isStr = lambda f: not f[:-5].isdigit()
		# Get JSON files
		files = os.listdir(self._presetsDir)
		files = filter(isJson, files)
		# Separate numbered file names from string files names. They should be sorted separately
		numberedFiles = []
		stringFiles = []
		for fName in files:
			withoutExt = fName[:-5] # Remove json from the end
			# I know this is not PyThOnIc. I don't need all these stupid exception b/c I actually have useful exceptions in my algorithm
			if withoutExt.isdigit():
				withoutExt = int(withoutExt) # convert to int or raise exception (meaning it's a string)
				numberedFiles.append(withoutExt)
			else:
				stringFiles.append(fName)
		# Sort files: string files names first, numbered test cases second
		numberedFiles = ["%d.json" % fName for fName in sorted(numberedFiles)]
		stringFiles = sorted(stringFiles)
		return stringFiles + numberedFiles

	def createDropdown(self):
		options = self._getJsonPresets()
		self.chosenPreset.set(options[0])
		self.presets = tk.OptionMenu(self.master, self.chosenPreset, *options)
		self.presets.pack(side=tk.TOP)

		self.loadPresetBtn = tk.Button(self)
		self.loadPresetBtn["text"] = "Load Preset"
		self.loadPresetBtn["command"] = self.loadPreset
		self.loadPresetBtn.pack(side=tk.TOP)

	def loadPreset(self):
		mapPath = self.chosenPreset.get()
		mapPath = os.path.join(self._presetsDir, mapPath)
		mapPath = os.path.abspath(mapPath)
		self.readMapJson(mapPath)

	def createButtons(self):
		self.browseBtn = tk.Button(self)
		self.browseBtn["text"] = "Select Map Json"
		self.browseBtn["command"] = self.selectMapFile
		self.browseBtn.pack(side=tk.TOP)

		heuristics = ["_heuristicNone", "_heuristicLineDist", "_heuristicShortestPath", "_heuristicTrmpp"]
		self.chosenHeuristic.set(heuristics[2])
		self.heuristics = tk.OptionMenu(self.master, self.chosenHeuristic, *heuristics)
		self.heuristics.pack(side=tk.TOP)

		self.runBtn = tk.Button(self)
		self.runBtn["state"] = tk.DISABLED
		self.runBtn["text"] = "A*"
		self.runBtn["command"] = self.run
		self.runBtn.pack(side=tk.TOP)

		self.runDpBtn = tk.Button(self)
		self.runDpBtn["state"] = tk.DISABLED
		self.runDpBtn["text"] = "DP"
		self.runDpBtn["command"] = self.runDp
		self.runDpBtn.pack(side=tk.TOP)

	def selectMapFile(self):
		mapPath = filedialog.askopenfilename(initialdir=self._presetsDir, title="Select Map", filetypes=(("JSON Files", "*.json"),)) # The trailing comma in filetypes is needed
		if (not mapPath):
			return
		mapPath = os.path.abspath(mapPath)
		self.readMapJson(mapPath)

	def readMapJson(self, absolutePath):
		if (not os.path.isfile(absolutePath)):
			return
		self.canvas.buildPreset(absolutePath)
		print("Max L = %.2f" % self.canvas.model.MAX_CABLE)
		self.runBtn["state"] = tk.NORMAL
		self.runDpBtn["state"] = tk.NORMAL

	def createDebugOptions(self):
		for (text, variable) in self._dbg.items():
			checkbox = tk.Checkbutton(master=self.master, text=text, variable=variable)
			checkbox.pack(side=tk.TOP)

	def run(self):
		if self.shouldDebugVisGraph:
			processReducedVisibilityGraph(True)
		elif not self.shouldDebugTighten and self.shouldDebugTriangulation:
			(cable, dest1, dest2) = (self.canvas.model.cable, self.canvas.model.robots[0].destination, self.canvas.model.robots[1].destination)
			(cable, dest1, dest2) = preprocessTheCable(cable, dest1, dest2)
			(cable, dest1, dest2) = pushCableAwayFromObstacles(cable, dest1, dest2)
			tri = testTriangulation(cable, dest1, dest2)
			print("triangles:", tri.triangleCount)
		elif self.shouldDebugTighten:
			cable = testTightenCable(self.shouldDebugTriangulation)
			self.canvas._renderCable(cable)
		else:
			solution = aStar(self.chosenHeuristic.get() ,self.debugFlag)
			self.canvas.renderSolution(solution, True)
		# Disable the button to force a reset
		self.runBtn["state"] = tk.DISABLED
		self.runDpBtn["state"] = tk.DISABLED


	def runDp(self):
		solution = dynamicProg(self.chosenHeuristic.get() ,self.debugFlag)
		self.canvas.renderSolution(solution, True)
		# Disable the button to force a reset
		self.runBtn["state"] = tk.DISABLED
		self.runDpBtn["state"] = tk.DISABLED
