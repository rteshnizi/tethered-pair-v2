import os
import tkinter as tk
from tkinter import filedialog

from .canvas import Canvas

cwd = os.path.dirname(__file__)
presetsDir = os.path.join(cwd, "..", "presets")

class Application(tk.Frame):
	def __init__(self):
		self.master = tk.Tk()
		self.master.title("Tethered Pair Simulation")
		self.master.geometry("1100x800")
		super().__init__(self.master)
		self.pack()
		self.createInputSelector()
		self.canvas = Canvas(self.master)

	def createInputSelector(self):
		self.browseBtn = tk.Button(self)
		self.browseBtn["text"] = "Select Map Json"
		self.browseBtn["command"] = self.readMapJson
		self.browseBtn.pack(side=tk.TOP)

	def readMapJson(self):
		mapPath = filedialog.askopenfilename(initialdir = presetsDir, title = "Select Map", filetypes = (("JSON Files", "*.json"),)) # The trailing comma in filetypes is needed
		if (not mapPath):
			return
		mapPath = os.path.abspath(mapPath)
		self.canvas.parseJson(mapPath)
