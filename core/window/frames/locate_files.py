import os
import tkinter as tk
from tkinter import ttk
import threading
from dataclasses import dataclass
from core import Helper as h
from .destination_drive import DestinationDrive
from .models.buttons.primary import PrimaryButton
from .models.text.info import InfoText
from .models.progressbar import Progressbar

@dataclass
class Layout():
	header_row				= 0
	header_row_title 		= 0
	header_row_separator	= 1

	body_row				= 1
	body_row_progressbar	= 0

	footer_row 				= 2
	footer_row_buttons 		= 0

class LocateFiles(ttk.Frame):

	def __init__(self, root_frame):
		super().__init__(root_frame)

		# System
		self.app 					= self.winfo_toplevel()
		self.root_frame 			= root_frame
		self.folder_found 			= 0
		self.files_found 			= 0

		self.header 				= None
		self.body 					= None
		self.footer 				= None
		self.button_frame 			= None
		self._button_index 			= 0

		# Draw UI
		self._render_UI()

		# Run main process
		self._run_process()

	def _render_UI(self):

		# Render header | body | footer
		self._render_header()
		self._render_body()
		self._render_footer()

		# Create buttons
		self._render_button('back_btn', PrimaryButton, text='Back', state='normal', command=self._command_back_button)
		self._render_button('start_btn', PrimaryButton, text='Start', state='normal', command=self._command_start_button)

	def _render_header(self):

		# Make self x-axis expandable on header row
		self.grid_columnconfigure(Layout.header_row, weight=1)

		# Render header, expanding x-axis, non-expanding y-axis
		self.header = ttk.Frame(self)
		self.header.grid(row=Layout.header_row, column=0, sticky='nsew')
		self.header.grid_columnconfigure(0, weight=1)

		# Render headline
		headline_text = 'Locate media files on: '
		headline_text_high = self.app.get_metadata('selected_drive').name
		headline = InfoText(self.header, text=headline_text, high_text=headline_text_high)
		headline.grid(row=Layout.header_row_title, column=0, padx=10, pady=10, sticky='w')

		# Horizontal line separator
		separator = ttk.Separator(self.header, orient='horizontal')
		separator.grid(row=Layout.header_row_separator, column=0, sticky='new')

	def _render_body(self):

		# Make self y-axis large expanding on body row
		self.grid_rowconfigure(Layout.body_row, weight=15)

		# Render body, expanding x-axis, large expanding y-axis
		self.body = ttk.Frame(self)
		self.body.grid(row=Layout.body_row, column=0, sticky='nsew')
		self.body.grid_columnconfigure(0, weight=1)
		self.body.grid_rowconfigure(Layout.body_row, weight=1)

	def _render_footer(self):

		# Make self y-axis expandable on footer row
		self.grid_rowconfigure(Layout.footer_row, weight=1)

		# Render footer, expanding x-axis, expanding y-axis
		self.footer = ttk.Frame(self)
		self.footer.grid(row=Layout.footer_row, column=0, sticky='nsew')
		self.footer.grid_columnconfigure(0, weight=1)
		self.footer.grid_rowconfigure(Layout.footer_row, weight=1)

	def _run_process(self):

		self.identify_file_locations()

	def _render_button(self, key, Button, text, state, command):

		# Create single button frame
		if not self.button_frame:
			self.button_frame = ttk.Frame(self.footer)
			self.button_frame.grid(row=Layout.footer_row_buttons, column=0, sticky='se')

		# Add button to existing frame
		btn = Button(self.button_frame, text=text, state=state, command = command)
		setattr(self, key, btn)

		# Increment button index and add frame
		btn.grid(row=0, column=self._button_index, padx=5, pady=5)
		self._button_index += 1

	def identify_file_locations(self):

		def finish_task():
			self.progressbar.update_progress('', 100)
			self.progressbar.add_status_text(text='Found ', clear=True)
			self.progressbar.add_status_text_highlighted(text=self.folder_found, type='success')
			self.progressbar.add_status_text(text=' folder(s) including ')
			self.progressbar.add_status_text_highlighted(text=self.files_found, type='success')
			self.progressbar.add_status_text(text=' file(s).', render=True)

			# Update <<start>> button
			self.start_btn.set_text('Continue')
			self.start_btn.set_command(self._command_next_button)
			self.back_btn.enable()
			self.start_btn.enable()

		def run_task():

			# Disable <<back>> and <<start>> button
			self.back_btn.disable()
			self.start_btn.disable()

			# Run task and save result in root window
			path_to_medias = drive.identify_media_file_locations(self)
			self.app.set_metadata('path_medias_to_copy', path_to_medias)

			# When finished, run callback
			self.app.after(0, finish_task)

		# Get drive from root
		drive = self.app.get_metadata('selected_drive')

		# Title row with percentage
		self.progressbar = Progressbar(self.body, title='')
		self.progressbar.grid(row=Layout.body_row_progressbar, column=0, columnspan=2, sticky='ew')
		self.progressbar.columnconfigure(0, weight=1)

		# Render progress bar
		self.progressbar.render_progress_bar()
		self.progressbar.set_count(0)

		# Process threading
		threading.Thread(target=run_task, daemon=True).start()

	""" Button commands """
	def _command_start_button(self):
		self.identify_file_locations()

	def _command_back_button(self):
		self.app.show_frame('SourceDirectory', reinit=True)

	def _command_next_button(self):
		self.app.render_new_frame(DestinationDrive, 'DestinationDrive', reinit=True)