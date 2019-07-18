import os
import tkinter as tk
from tkinter import filedialog

from gui.canvas import Canvas
from algorithm.aStar import aStar

cwd = os.path.dirname(__file__)
presetsDir = os.path.join(cwd, "..", "presets")

class Application(tk.Frame):
	def __init__(self):
		self.master = tk.Tk()
		self.master.title("Tethered Pair Simulation")
		self.master.geometry("1100x800")
		super().__init__(self.master)
		self.pack()
		self.chosenPreset = tk.StringVar(master=self.master)
		self.createDropdown()
		self.createButtons()
		self.canvas = Canvas(self.master)

	def createDropdown(self):
		options = os.listdir(presetsDir)
		self.chosenPreset.set(options[0])
		self.presets = tk.OptionMenu(self.master, self.chosenPreset, *options)
		self.presets.pack(side=tk.TOP)

		self.loadPresetBtn = tk.Button(self)
		self.loadPresetBtn["text"] = "Load Preset"
		self.loadPresetBtn["command"] = self.loadPreset
		self.loadPresetBtn.pack(side = tk.TOP)

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
		self.runBtn.pack(side = tk.TOP)

	def selectMapFile(self):
		mapPath = filedialog.askopenfilename(initialdir=presetsDir, title="Select Map", filetypes=(("JSON Files", "*.json"),)) # The trailing comma in filetypes is needed
		if (not mapPath):
			return
		mapPath = os.path.abspath(mapPath)
		self.readMapJson(mapPath)

	def readMapJson(self, absolutePath):
		if (not os.path.isfile(absolutePath)):
			return
		self.canvas.parseJson(absolutePath)
		self.runBtn["state"] = tk.NORMAL

	def run(self):
		aStar()
