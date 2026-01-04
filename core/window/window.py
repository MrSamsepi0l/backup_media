import os
from core import Helper as h
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from core.setup.setup import setup
from core.window.frames.root_frame import RootFrame
from core.window.frames.source_drive import SourceDrive
from .frames.locate_files import LocateFiles
from .frames.destination_drive import DestinationDrive
from .frames.inspection import Inspection
from .frames.copy import Copy

class Window(tk.Tk):
	"""Root window"""

	def __init__(self):
		super().__init__()

		# Metadata collected while processing
		self.metadata = {
			'selected_drive'				: None,
			'path_medias_to_copy'			: None,
			'target_drive'					: None,
			'unique_medias'					: [],
			'duplicate_medias'				: [],
		}

		# List of available frames and if they should be created on init
		self.frame_lib = [

			# Class   						 Name   				Render on init
			(RootFrame, 					'RootFrame',			True),
			(SourceDrive, 					'SourceDirectory',		True),
			(LocateFiles, 					'LocateFiles',		 	False),
			(DestinationDrive,				'DestinationDrive',		False),
			(Inspection,					'Inspection',			False),
			(Copy, 							'Copy',					False),

		]

		# Init process, start and stay in program GUI
		self._render_window()
		self.mainloop()

	##############################################
	#				Internal usage				 #
	##############################################
	def _render_window(self):

		# Configure main window
		title = setup.get_program_title()
		self.title(title)
		self.image_path = os.path.join('data', 'public', 'image', 'header_bg_image.jpg')
		self.window_width = 700
		self.window_height = 550
		self.minsize(self.window_width, self.window_height)
		self.screen_width = self.winfo_screenwidth()
		self.screen_height = self.winfo_screenheight()
		x = (self.screen_width / 2) - (self.window_width / 2)
		y = (self.screen_height / 2) - (self.window_height / 2)
		self.geometry('%dx%d+%d+%d' % (self.window_width, self.window_height, x, y))

		self.container = ttk.Frame(self, padding=10)
		self.container.grid(row=1, column=0, sticky='nsew')

		# Make container rows/columns expandable
		self.container.grid_rowconfigure(0, weight=0)  	# ROW = 0 = header
		self.container.grid_rowconfigure(1, weight=1) 	# ROW = 1 = body (expands)
		# self.container.grid_rowconfigure(2, weight=1)	# ROW = 2 = footer
		self.container.grid_columnconfigure(0, weight=1)

		# Make self expandable
		self.grid_rowconfigure(0, weight=0)		# header row: fixed
		self.grid_rowconfigure(1, weight=1)		# container row: expands
		self.grid_columnconfigure(0, weight=1)

		# Render Favicon and header
		self._set_root_icon()
		self._render_header()

		# Create frames
		self._init_frames()

	def _set_root_icon(self):

		# Load image
		image_path = os.path.join(h.get_base_path(), 'data', 'public', 'image', 'root_favicon.png') # Absolute path
		# image_path = os.path.join('data', 'public', 'image', 'root_favicon.png') # Relative path

		# Convert to PhotoImage
		image = Image.open(image_path)
		photo = ImageTk.PhotoImage(image)

		# Set in window
		self.iconphoto(True, photo)
		self._icon_photo = photo

	def _init_frames(self):
		self.frames = {}

		# Run frame lib
		for F, name, on_init in self.frame_lib:

			# Skip frames that should not be created on init
			if not on_init:
				continue

			frame = F(self.container)  # pass controller to frame
			self.frames[name] = frame
			frame.grid(row=1, column=0, sticky='nsew')

	def _render_header(self):

		self.header = ttk.Frame(self, relief='raised')
		self.header.grid(row=0, column=0, sticky='nsew') # full width
		self.header.grid_rowconfigure(0, weight=1)
		self.header.grid_columnconfigure(0, weight=1)	# center content horizontally

		# Load image
		self.original_image = Image.open(self.image_path)

		# Canvas for background image
		self.canvas = tk.Canvas(self.header, height=140, highlightthickness=0)
		self.canvas.grid(row=0, column=0, sticky='nsew')

		# Draw image and bind event
		self.image_text = self.canvas.create_text(0, 0, text = setup.config.get_program_title().upper(), font=("Arial", 18, 'bold'), fill='white', anchor='center')
		self.canvas.bind('<Configure>', self.__resize_image)


	##############################################
	#				Public usage				 #
	##############################################
	def set_metadata(self, key, val):
		self.metadata[key] = val

	def get_metadata(self, key):
		return self.metadata.get(key)

	def show_frame(self, name, reinit=False):

		# Get frame from list and bringt it up
		if not reinit:
			frame = self.frames[name]
			frame.tkraise()
			return

		# Otherwise search for matching frame in list, overwrite and re-create it
		for Frame, cl_name, on_init in self.frame_lib:
			if cl_name == name:
				frame = Frame(self.container)
				self.frames[cl_name] = frame
				frame.grid(row=1, column=0, sticky='nsew')

	def render_new_frame(self, frame_class, name=None, reinit=False, **kwargs):
		"""
		Instantiates a new frame - not like the pre-created frames
		that are already initialized
		"""

		frame_name = name or frame_class.__name__
		if not reinit and frame_name in self.frames:
			return self.frames[frame_name]

		frame = frame_class(self.container, **kwargs)
		self.frames[frame_name] = frame
		frame.grid(row=1, column=0, stick='nsew') # Stack frames
		return frame


	##############################################
	#				Event Bindings				 #
	##############################################
	def __resize_image(self, event, mode='cover'):
		canvas_w = event.width
		canvas_h = event.height

		img = self.original_image.copy()

		if mode == "contain":
			img.thumbnail((canvas_w, canvas_h), Image.LANCZOS)

		elif mode == "cover":
			img_ratio = img.width / img.height
			canvas_ratio = canvas_w / canvas_h

			if canvas_ratio > img_ratio:
				new_w = canvas_w
				new_h = int(canvas_w / img_ratio)
			else:
				new_h = canvas_h
				new_w = int(canvas_h * img_ratio)

			img = img.resize((new_w, new_h), Image.LANCZOS)

			# Crop center
			left = (new_w - canvas_w) // 2
			top = (new_h - canvas_h) // 2
			img = img.crop((left, top, left + canvas_w, top + canvas_h))

		self.bg_image = ImageTk.PhotoImage(img)

		self.canvas.delete('bg')
		self.canvas.create_image(canvas_w // 2, canvas_h // 2, image=self.bg_image, anchor='center', tags='bg')

		# Center text
		self.canvas.coords(self.image_text, canvas_w // 2, canvas_h // 2)

		# Ensure text is above image
		self.canvas.tag_raise(self.image_text)