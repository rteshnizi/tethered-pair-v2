import os
import tkinter as tk
from tkinter import filedialog

from gui.canvas import Canvas
from algorithm.aStar import aStar
from algorithm.cableAlgorithms import testTightenCable
from algorithm.triangulation import testTriangulation

cwd = os.path.dirname(__file__)
presetsDir = os.path.join(cwd, "..", "presets")

class TetheredPairApp(tk.Frame):
	def __init__(self):
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

	def createDropdown(self):
		options = sorted(os.listdir(presetsDir))
		self.chosenPreset.set(options[0])
		self.presets = tk.OptionMenu(self.master, self.chosenPreset, *options)
		self.presets.pack(side=tk.TOP)

		self.loadPresetBtn = tk.Button(self)
		self.loadPresetBtn["text"] = "Load Preset"
		self.loadPresetBtn["command"] = self.loadPreset
		self.loadPresetBtn.pack(side=tk.TOP)

	def loadPreset(self):
		mapPath = self.chosenPreset.get()
		mapPath = os.path.join(presetsDir, mapPath)
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
		mapPath = filedialog.askopenfilename(initialdir=presetsDir, title="Select Map", filetypes=(("JSON Files", "*.json"),)) # The trailing comma in filetypes is needed
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
			finalCable = testTightenCable(self.shouldDebugTriangulation)
			self.canvas.renderSolution(finalCable)
		else:
			finalCable = aStar()
			self.canvas.renderSolution(finalCable)
		# Disable the button to force a reset
		self.runBtn["state"] = tk.DISABLED
