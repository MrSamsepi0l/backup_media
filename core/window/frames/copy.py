import os
import tkinter as tk
import shutil
import threading
from tkinter import ttk
from data.media import Media
from core.helper import Helper as h
from .models.text.info import InfoText
from .models.buttons.primary import PrimaryButton
from .models.progressbar import Progressbar
from .sync import Sync

class Copy(ttk.Frame):

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
		# ttk.Label(self, text="Detected duplicate and unique media files", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")

		# Add buttons to footer
		self._render_button('back_btn', PrimaryButton, 'Back', 'normal', self._command_back_button)
		self._render_button('sync_btn', PrimaryButton, 'Sync with backup drive?', 'disabled', self._command_sync_button)

	def _run_process(self):

		# Delete duplicate folder with progress status and finish message
		self._delete_duplicate_folder()

		# Copy unique media files to destination with progress and finish message
		self._copy_unique_medias_files()

		# Finish execution or continue with backup sync

	def _copy_unique_medias_files(self):

		# Create media object
		unique_media = Media(path=self.app.metadata['target_drive'])

		# Set folder where fils will be saved (create if not existing)
		target_save_folder = unique_media._create_target_save_folder()
		if not target_save_folder:
			return

		# Init progressbar
		progressbar = Progressbar(self, title=f'Copying unique media files to destination...')
		progressbar.grid(row=2, column=0, columnspan=2, sticky='ew')
		progressbar.columnconfigure(0, weight=1)

		# Calculate total
		total = len(self.app.metadata['unique_medias']) or 0

		def run_task():

			unique_media_files = self.app.metadata['unique_medias']
			for idx, file in enumerate(unique_media_files.items(), start=1):

				name, path = file
				print(f'Copy file ({path}) to {target_save_folder}')
				# Copy medias into folder
				shutil.copy2(path, target_save_folder)

				percent = int(idx / total * 100)
				progressbar.update_progress(name, percent=percent)

			# Run finishing callback
			self.app.after(0, finish_task)

		def finish_task():
			progressbar.update_progress('', 100)
			progressbar.set_success_status_text(f'Finished!')
			text = InfoText(self, text=f'Copied all ({len(self.app.metadata['unique_medias'])}) unique media files to: ', high_text=target_save_folder)
			text.grid(row=3, column=0, columnspan=3, sticky='w', padx=10, pady=5)
			self.sync_btn.enable()
			self._delete_temp_dir()

		# Render progress bar
		progressbar.render_progress_bar()
		progressbar.set_count(0)

		# Process threading
		threading.Thread(target=run_task, daemon=True).start()

	def _delete_temp_dir(self):

		# Delete temp folder if not already done
		drive = self.app.metadata['selected_drive']

		# Process threading
		threading.Thread(target=drive.delete_temp_dir(), daemon=True).start()

	def _delete_duplicate_folder(self):

		# TODO? remove while no folder is created?
		# Delete folder
		target_drive = self.app.metadata['target_drive']
		print(f'DEBUG: Would delete duplicate folder here')
		# target_drive.delete_duplicate_folder()





	def _render_button(self, key, Button, text, state, command):

		# Create button in recently created or existing frame
		btn = Button(self.footer, text=text, state=state, command=command)
		setattr(self, key, btn)

		# Configure button layout and increment index
		btn.grid(row=0, column=self._footer_idx, padx=5, pady=5)
		self._footer_idx += 1

	def _command_back_button(self):
		self.app.show_frame('Inspection')

	def _command_sync_button(self):

		self.app.render_new_frame(Sync, 'Sync', reinit=True)