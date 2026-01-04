import os
import tkinter as tk
from tkinter import ttk

class RootFrame(ttk.Frame):
	""" Root window """

	def __init__(self, root_frame):
		super().__init__(root_frame)

		# System
		self.app = self.winfo_toplevel()
		self.root_frame = root_frame

		# main_font = root_window.main_font

		ttk.Label(self, text="Main View").pack(pady=20)
		self.show_btn = ttk.Button(self, text="Show directories", command = lambda: self.app.show_frame('SourceDirectory'))
		self.show_btn.pack(pady=5)


	def init(self):
		pass