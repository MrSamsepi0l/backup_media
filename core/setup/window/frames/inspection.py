import os
import tkinter as tk
from tkinter import ttk
from core.helper import Helper as h
from data.media import Media
from .models.image_list import ImageList
from .models.buttons.primary import PrimaryButton
from .models.text.info import InfoText
from .copy import Copy
from .sync import Sync

class Inspection(ttk.Frame):

	def __init__(self, root_frame):
		super().__init__(root_frame)

		# System
		self.app = self.winfo_toplevel()		# equals root_window
		self.root_frame = root_frame
		self.button_frame = None

		# Draw UI
		self._render_UI()

		# Run main process
		self._run_process()


	def _render_UI(self):

		# Expand column
		self.grid_columnconfigure(0, weight=1)
		# ttk.Label(self, text="Detected duplicate and unique media files", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")

		self._render_button('back_btn', PrimaryButton, 'Back', 'normal', 8, self._command_back_button)
		self._render_button('next_btn', PrimaryButton, 'Continue', 'normal', 8, self._command_next_button)

	def _run_process(self):

		# Create media object
		medias_to_copy = Media(path = self.app.metadata['path_medias_to_copy'])

		# Create media object with target drive (where to store the media files)
		destination_drive = Media(path = self.app.metadata['target_drive'])

		# Search for unique and duplicate media files
		unique_medias, duplicate_medias = h.compare_dictionaries(medias_to_copy.load_media_files(), destination_drive.load_media_files())

		# Render unique and duplicate medias
		self._render_unique_images(unique_medias)
		self._render_duplicate_images(duplicate_medias)

		if not unique_medias:
			self.next_btn.set_text('Sync with backup drive?')
			self.next_btn.set_command(self._command_sync_button)

		# Save global
		self.app.set_metadata('unique_medias', unique_medias)
		self.app.set_metadata('duplicate_medias', duplicate_medias)

		# If no unique or duplicate medias found, delete temp folder
		if not unique_medias and not duplicate_medias:
			drive = self.app.metadata['selected_drive']
			drive.delete_temp_dir()

	def _render_unique_images(self, unique_medias):

		# Create text widget
		text_frame = ttk.Frame(self)
		text_frame.grid(row=2, column=0, sticky='nsew')
		text = InfoText(text_frame, text='Unique medias found to copy: ', high_text=len(unique_medias))
		text.grid(row=0, column=0, padx=5, pady=5, sticky="w")

		# Separator over complete frame
		separator = ttk.Separator(self, orient="horizontal")
		separator.grid(row=3, column=0, sticky="new")

		# If no unique medias found - nothing to render
		if not unique_medias:
			return

		# Create instance
		self.uniq_media = ImageList(self, image_size=100)

		# Grid layout for scrollbar and canvas
		self.uniq_media.grid(row=4, column=0, sticky='nsew')

		self.grid_rowconfigure(2, weight=1)
		self.grid_columnconfigure(0, weight=1) # Expand on x-axis to the right

		# Update scroll region when frame size changes
		self.uniq_media.image_frame.bind('<Configure>', self.uniq_media._on_frame_configure)
		self.uniq_media.canvas.bind('<Enter>', self.uniq_media._bind_mousewheel)
		self.uniq_media.canvas.bind('<Leave>', self.uniq_media._unbind_mousewheel)

		# Load images
		sorted_list = sorted(unique_medias.items(), key=lambda x: x[0])

		# Load images asnyc in background thread
		self.uniq_media._load_image_async(sorted_list)

	def _render_duplicate_images(self, duplicate_medias):

		# Create text widget (duplicate medias)
		text_frame = ttk.Frame(self)
		text_frame.grid(row=5, column=0, sticky='nsew')
		text_widget = InfoText(text_frame, text='Duplicate medias found to check: ', high_text=len(duplicate_medias))
		text_widget.grid(row=0, column=0, padx=5, pady=5, sticky="w")

		# Separator over complete frame
		separator = ttk.Separator(self, orient="horizontal")
		separator.grid(row=6, column=0, sticky="new")

		# If no duplicate medias found - nothing to render
		if not duplicate_medias:
			return

		# Create instance
		self.dup_media = ImageList(self, image_size=100)

		# Grid layout for scrollbar and canvas
		self.dup_media.grid(row=7, column=0, sticky='nsew')
		self.grid_rowconfigure(7, weight=1)
		self.grid_columnconfigure(0, weight=1) # Expand on x-axis to the right

		# Update scroll region when frame size changes
		self.dup_media.image_frame.bind('<Configure>', self.dup_media._on_frame_configure)
		self.dup_media.canvas.bind('<Enter>', self.dup_media._bind_mousewheel)
		self.dup_media.canvas.bind('<Leave>', self.dup_media._unbind_mousewheel)

		# Load images
		sorted_list = sorted(duplicate_medias.items(), key=lambda x: x[0])

		# Load images asnyc in background thread
		self.dup_media._load_image_async(sorted_list)

	def _render_button(self, key, Button, text, state, row, command):

		# Create single button frame
		if not self.button_frame:
			self.button_frame = ttk.Frame(self)
			self.button_frame.grid(row=row, column=0, columnspan=2, sticky='ew')

			self.button_frame.grid_columnconfigure(0, weight=5) # left spacer expanding
			self._button_index = 1

		# Create button in recently created or existing frame
		btn = Button(self.button_frame, text=text, state=state, command=command)
		setattr(self, key, btn)

		# Configure button layout and increment index
		btn.grid(row=0, column=self._button_index, padx=5, pady=5)
		self._button_index += 1

	def _command_back_button(self):
		self.app.show_frame('DestinationDrive')

	def _command_next_button(self):

		# If we have unique medias to copy
		if self.app.metadata['unique_medias']:
			self.app.render_new_frame(Copy, 'Copy', reinit=True)

	def _command_sync_button(self):

		# If we don't have unique medias to copy
		if not self.app.metadata['unique_medias']:
			self.app.render_new_frame(Sync, 'Sync', reinit=True)

