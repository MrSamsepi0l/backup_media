import os
import tkinter as tk
import threading
from tkinter import ttk
from data.drive import Drive
from core.helper import Helper as h
from .models.text.info import InfoText
from .models.buttons.primary import PrimaryButton
from .models.progressbar import Progressbar

class Sync(ttk.Frame):

	def __init__(self, root_frame):
		super().__init__(root_frame)

		# System
		self.app = self.winfo_toplevel()
		self.root_frame = root_frame
		self.footer = None
		self.footer_row = 5
		self._footer_idx = 0

		# Draw UI
		self._render_UI()

		# Run main process
		self._run_process()


	def _render_UI(self):

		# Create footer
		if not self.footer:
			self.footer = ttk.Frame(self)
			self.footer.grid(row=self.footer_row, column=0, columnspan=2, sticky='ew')
			self.footer.grid_columnconfigure(0, weight=5) # left spacer expanding
			self._footer_idx = 1

		# Expand column
		self.grid_columnconfigure(0, weight=1)

		# Add buttons to footer
		self._render_button('back_btn', PrimaryButton, 'Back', 'normal', self._command_back_button),
		self._render_button('next_btn', PrimaryButton, 'Continue', 'normal', self._command_next_button),

	def _run_process(self):
		pass

	def _render_button(self, key, Button, text, state, command):

		# Create button in recently created or existing frame
		btn = Button(self.footer, text=text, state=state, command=command)
		setattr(self, key, btn)

		# Configure button layout and increment index
		btn.grid(row=0, column=self._footer_idx, padx=5, pady=5)
		self._footer_idx += 1

	def _command_back_button(self):

		# If unique medias existing - go back to copy frame
		if self.app.metadata['unique_medias']:
			self.app.show_frame('Copy')

		# Otherwise to inspection
		else:
			self.app.show_frame('Inspection')

	def _command_next_button(self):
		pass