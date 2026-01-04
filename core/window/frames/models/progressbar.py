import os
import tkinter as tk
from tkinter import ttk
from core.setup.design import WindowDesign

class Style(WindowDesign):

	# Progress Bar
	fg_bar 					= WindowDesign.main['true_azure']

	# Title
	font_title				= ('Segoe UI', 10, 'bold')
	font_title_highlight	= ('Segoe UI', 10, 'bold')
	fg_title				= WindowDesign.main['ink_black']
	fg_title_highlight 		= {
		'default'			: "#4684BB",
		'processing'		: '#B1638E',
		'success'			: "#B1638E",
		'error'				: '',
		'summary'			: '',
	}

	# Status
	font_status 			= ('Segoe UI', 10)
	font_status_highlight	= ('Segoe UI', 10, 'bold')
	fg_status 				= WindowDesign.main['charcoal_brown']
	fg_status_highlight 	= {
		'default'			: '#77F3F3',
		'processing'		: "#6B093F",
		'success'			: WindowDesign.main['oxford_navy'],
		'error'				: '',
		'summary'			: '',
	}

	# Percent display
	font_perc_label 		= ('Segoe UI', 10)
	fg_perc_label 			= '#666666'



class Progressbar(ttk.Frame):

	def __init__(self, parent, title=None):
		super().__init__(parent)

		self.app = self.winfo_toplevel()
		self.title = None
		self.status = None
		self.count = tk.IntVar(value = 0)
		self.canvas = None
		self.percent_label = None

	def add_status_text_highlighted(self, text, type='default', clear=False, render=False):

		# Configure highlight color based on given type and add colored text
		self.status.tag_configure('status_highlight', foreground=Style.fg_status_highlight[type], font=Style.font_status_highlight)
		self.add_status_text(text, highlight=True, clear=clear, render=render)

	def add_status_text(self, text, highlight=False, clear=False, render=False):

		self.status.config(state='normal')

		# If new status
		if clear:
			self.status.delete('1.0', 'end')

		# Add partial text to status text
		self.status.insert('end', text, 'status_highlight' if highlight else 'base_color')
		if render:
			self.status.config(state='disabled')

		# # Show text if wanted, otherwise hide it
		# if render:
		# 	self.status.grid()
		# else:
		# 	self.status.grid_remove()

	def add_title_text_highlighted(self, text, type='default', clear=False, render=False):

		# Configure highlight color based on given type and add colored text
		self.title.tag_configure('title_highlight', foreground=Style.fg_title_highlight[type])
		self.add_title_text(text, highlight=True, clear=clear, render=render)

	def add_title_text(self, text, highlight=False, clear=False, render=False):

		self.title.config(state='normal')

		# If new title
		if clear:
			self.title.config(state='normal')
			self.title.delete('1.0', 'end')

		# Add partial text to title text
		self.title.insert('end', text, 'title_highlight' if highlight else 'base_color')
		self.title.config(state='disabled')

		# Show text if wanted, otherwise hide it
		if render:
			self.title.pack(side=tk.LEFT)
		else:
			# self.title.config(state='disabled')
			self.title.pack_forget()


	def set_count(self, count):
		self.count.set(count)

	def set_percent_label(self, percent):
		self.percent_label.config(text=f'{percent} %')

	# Progress bar frame
	def render_progress_bar(self):

		# Title row with percentage
		title_frame = tk.Frame(self, bg=WindowDesign.main['bg'])
		title_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
		title_frame.columnconfigure(0, weight=1)

		# Title
		self.title = tk.Text(title_frame, height=1, borderwidth=0, highlightthickness=0, bg=WindowDesign.main['bg'], font=Style.font_title)
		self.title.tag_configure('base_color', foreground=Style.fg_title)
		self.title.pack(side=tk.LEFT)

		# Percentage label
		self.percent_label = tk.Label(
			title_frame,
			text='0 %',
			anchor='e',
			font=Style.font_perc_label,
			fg=Style.fg_perc_label,
			bg=WindowDesign.main['bg']
		)
		self.percent_label.pack(side=tk.RIGHT)

		# Canvas-based progress bar
		self.canvas = tk.Canvas(
			self,
			height=24,
			bg=WindowDesign.main['bg'],
			highlightthickness=0,
		)
		self.canvas.grid(row=3, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

		# Background
		self.progress_bg = self.canvas.create_rectangle(0, 2, 100, 22, fill=WindowDesign.main['bg'], outline='#e0e0e0', width=1)

		# Progress bar
		self.progress_rect = self.canvas.create_rectangle(0, 2, 0, 22, fill=Style.fg_bar, outline='') # old blue: #4C93AF

		# Spacer row (always present)
		self.status_spacer = ttk.Frame(self, height=36)
		self.status_spacer.grid(row=4, column=0, columnspan=2, sticky="ew")

		# Status text
		self.status = tk.Text(self, height=1, wrap='none', undo=False, borderwidth=0, highlightthickness=0, bg=WindowDesign.main['bg'])
		self.status.tag_configure('base_color', foreground=Style.fg_status, font=Style.font_status)
		self.status.grid(row=4, column=0, columnspan=2, sticky='ew', padx=10, pady=(5, 10))

		# Event binding for progress
		self.canvas.bind('<Configure>', self._update_custom_progress)

	def _update_custom_progress(self, *args):
		"""Update custom canvas progress bar"""
		width = self.canvas.winfo_width()
		if width < 1:
			return

		progress = self.count.get()
		fill_width = max(0, (width * progress) / 100)

		self.canvas.coords(self.progress_bg, 0, 2, width, 22)
		self.canvas.coords(self.progress_rect, 0, 2, fill_width, 22)

	def update_progress(self, text='', percent=0):
		"""Update progress bar with filename and percentage"""

		# Clamp percent between 0-100
		percent = max(0, min(100, percent))

		# Update progress value and percentage display
		self.set_count(percent)
		self.set_percent_label(percent)

		# Update status text if given
		if text:
			self.add_status_text(text='Processing: ', clear=True)
			self.add_status_text_highlighted(text=text, type='processing', render=True)

		# Update canvas
		self._update_custom_progress()

		# Force UI update
		self.update_idletasks()