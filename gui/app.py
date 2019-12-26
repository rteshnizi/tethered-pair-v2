import os
import tkinter as tk
from tkinter import filedialog

from gui.canvas import Canvas
from algorithm.aStar import aStar
from algorithm.cableAlgorithms import testTightenCable
from algorithm.triangulation import testTriangulation

class TetheredPairApp(tk.Frame):
	def __init__(self):
		self._presetsDir = os.path.join(os.path.dirname(__file__), "..", "presets")
		self.master = tk.Tk()
		self.master.title("Tethered Pair Simulation")
		self.master.geometry("1100x800")
		super().__init__(self.master)
		self.pack()
		self.chosenPreset = tk.StringVar(master=self.master)
		self._dbg = {
			'printMouseEvents': tk.IntVar(master=self.master, value=0),
			'runTriangulation': tk.IntVar(master=self.master, value=0),
			'runTighten': tk.IntVar(master=self.master, value=0)
		}
		self.createDropdown()
		self.createButtons()
		self.createDebugOptions()
		self.canvas = Canvas(self.master, self)

	@property
	def shouldPrintMouse(self) -> bool:
		return self._dbg['printMouseEvents'].get() == 1

	@property
	def shouldDebugTriangulation(self) -> bool:
		return self._dbg['runTriangulation'].get() == 1

	@property
	def shouldDebugTighten(self) -> bool:
		return self._dbg['runTighten'].get() == 1

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

		self.runBtn = tk.Button(self)
		self.runBtn["state"] = tk.DISABLED
		self.runBtn["text"] = "Run"
		self.runBtn["command"] = self.run
		self.runBtn.pack(side=tk.TOP)

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
		self.runBtn["state"] = tk.NORMAL

	def createDebugOptions(self):
		checkbox = tk.Checkbutton(master=self.master, text='Print Mouse', variable=self._dbg['printMouseEvents'])
		checkbox.pack(side=tk.TOP)
		checkbox = tk.Checkbutton(master=self.master, text='Test Triangulation', variable=self._dbg['runTriangulation'])
		checkbox.pack(side=tk.TOP)
		checkbox = tk.Checkbutton(master=self.master, text='Test Tighten Alg', variable=self._dbg['runTighten'])
		checkbox.pack(side=tk.TOP)

	def run(self):
		if not self.shouldDebugTighten and self.shouldDebugTriangulation:
			tri = testTriangulation()
			print("triangles:", tri.triangleCount)
		elif self.shouldDebugTighten:
			cable = testTightenCable(self.shouldDebugTriangulation)
			self.canvas._renderCable(cable)
		else:
			solutionNode = aStar()
			self.canvas.renderSolution(solutionNode)
		# Disable the button to force a reset
		self.runBtn["state"] = tk.DISABLED
