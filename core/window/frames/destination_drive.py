import os, sys
import string
import ctypes
import tkinter as tk
from tkinter import ttk
from core import Helper as h
from config import User
from core.setup.design import Design
from .inspection import Inspection
from .models.buttons.primary import PrimaryButton
from .models.text.info import InfoText

class DestinationDrive(ttk.Frame):

	def __init__(self, root_frame):
		super().__init__(root_frame)

		# System
		self.app = self.winfo_toplevel()
		self.root_frame = root_frame

		self.user = None

		# Layout
		self.head_row = None
		self.body_row = None
		self.foot_row = None
		self.button_frame = None
		self._button_index = 0
		self._dir_tree_hover_rowID = None

		# Process
		self.default_destination = None
		user = User()
		self.user = user
		self.default_destination = user.get_default_destination_drive()

		# Configure layout
		self.__configure_layout()

		# Draw UI
		self.render_UI()

	def __configure_layout(self):

		# Init rows
		self.head_row = 0
		self.body_row = 1
		self.foot_row = 4

		# Make self expanding
		self.grid_columnconfigure(self.head_row, weight=1)		# Expand header row
		self.grid_rowconfigure(self.body_row, weight=1)			# Expand content row
		self.grid_rowconfigure(self.foot_row, weight=0)			# Fixed buttons stay bottom

	# UI elements
	def render_UI(self):

		# Render header
		self._render_header()

		#
		self._render_drive_list()
		self.after(100, lambda: self._preselect_default_drive())

		# Render <<back>> button
		self._render_button('back_btn', PrimaryButton, 'Back', 'normal', self.foot_row, self._command_back_button)

		# Selection for taking default destination or not
		self._render_button('safe_btn', PrimaryButton, 'Safe as new default', ('disabled' if self.default_destination else 'normal'), self.foot_row, self._command_safe_button)
		self._render_button('next_btn', PrimaryButton, 'Continue', 'normal', self.foot_row, self._command_next_button)


	def _render_header(self):

		text = InfoText(self, text='Choose destination where to store media files.')
		text.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=5)

		separator = ttk.Separator(self, orient="horizontal")
		separator.grid(row=1, column=0, sticky="new")

		# If we have a default destination
		if self.default_destination:

			# Old padding: (10, 5)
			self.default_destination_text = InfoText(self, text=f'Current saved default destination: ', high_text=self.default_destination)
			self.default_destination_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="w")

			self.target_drive_text = InfoText(self, text='Auto selected default destination: ', high_text=self.default_destination)
			self.target_drive_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="w")

	def _update_target_drive_text(self):

		# Load metadata and update text
		target_drive = self.app.get_metadata('target_drive')
		self.target_drive_text.set_high_text(text=f'Selected destination: ', high_text=target_drive)

	def _update_default_destination_text(self):
		self.default_destination_text.set_high_text(text='Current saved default destination: ', high_text=self.default_destination)

	def _render_button(self, key, Button, text, state, row, command_fn):

		# Create single button frame
		if not self.button_frame:
			self.button_frame = ttk.Frame(self)
			self.button_frame.grid(row=row, column=0, sticky='se')
			# self.button_frame.grid_columnconfigure(0, weight=5) # left spacer expanding

		# Create button in recently created or existing frame
		btn = Button(self.button_frame, text=text, state=state, command = command_fn)
		setattr(self, key, btn)

		# Configure button layout and increment index
		btn.grid(row=0, column=self._button_index, padx=5, pady=5)
		self._button_index += 1

	def _render_drive_list(self):

		# TODO: export to outer configuration JSON layout or sth. to externally configure custom layouts
		style = ttk.Style()
		style.configure('Dark.Treeview', background=Design.dest_dir_tree['main_bg'], foreground='white', fieldbackground=Design.dest_dir_tree['main_bg'], rowheight=24, borderwidth=0)
		style.map('Dark.Treeview', background=[ ('selected', Design.dest_dir_tree['select_bg']) ])

		# Create frame
		tree_frame = ttk.Frame(self, padding=10)
		tree_frame.grid(row=2, column=0, sticky='nsew')
		tree_frame.grid_rowconfigure(0, weight=1)
		tree_frame.grid_columnconfigure(0, weight=1)

		# Tree view (modern list)
		self.dir_tree = ttk.Treeview(tree_frame, columns=('folder', 'files',), show='tree headings', style='Dark.Treeview', selectmode='browse')
		self.dir_tree.heading('#0', text='Folder')
		self.dir_tree.heading('files', text='Files')
		self.dir_tree.column('files', width=50, anchor='e')
		self.dir_tree.grid(row=0, column=0, sticky='nsew')
		self.dir_tree.tag_configure("hover", background=Design.dest_dir_tree['hover_bg'])  # hover row
		self.dir_tree.tag_configure("normal", background=Design.dest_dir_tree['main_bg'])  # normal row

		# Scrollbar configuration
		scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.dir_tree.yview)
		scrollbar.grid(row=0, column=1, sticky="ns")
		self.dir_tree.configure(yscrollcommand=scrollbar.set)

		# Bind events
		self.dir_tree.bind("<<TreeviewOpen>>", self._on_open)    # when expanding a folder
		self.dir_tree.bind("<<TreeviewSelect>>", self._event_select_item_in_list) # when selecting a folder
		self.dir_tree.bind("<Motion>", self._on_hover)

		# Load list of 'main' drives and insert them into the tree
		drive_list = self.get_windows_drives()
		for drive in drive_list:
			node = self.dir_tree.insert('', 'end', text=drive, values=(drive,))
			self.dir_tree.insert(node, 'end')

	def _preselect_default_drive(self):

		# If no default - nothing to do here
		if not self.dir_tree or not self.default_destination:
			return

		target_path = os.path.normpath(self.default_destination)
		parts = [p for p in target_path.split(os.sep) if p]  # remove empty strings

		parent_node = ''
		current_node = ''

		# Helper function
		def get_subfolders(parent_node, children):
			if children and self.dir_tree.item(children[0], 'text') == '':
				self.dir_tree.delete(children[0])
				path = self.dir_tree.item(parent_node, 'values')[0] if self.dir_tree.item(parent_node, 'values') else self.dir_tree.item(parent_node, 'text')
				self._insert_subfolders(self.dir_tree, parent_node, path)

		for part in parts:

			children = self.dir_tree.get_children(parent_node)
			if children:
				get_subfolders(parent_node, children)

			found = False
			for child in children:
				values = self.dir_tree.item(child, 'values')
				node_path = values[0] if values else self.dir_tree.item(child, 'text')
				node_path = os.path.normpath(node_path)

				# For root drive, remove trailing backslash if any
				if os.path.splitdrive(node_path)[1] == os.sep:
					node_path = os.path.splitdrive(node_path)[0]

				# Safe for drives
				node_name = os.path.basename(node_path) or node_path

				# Bring back the root drive backslash
				drive, tail = os.path.splitdrive(node_path)
				if drive and tail == '':
					node_path = drive + os.sep

				if node_name.lower() == part.lower():
					self.dir_tree.item(child, open=True)
					parent_node = child
					current_node = child
					found = True
					children = self.dir_tree.get_children(child)
					if children:
						get_subfolders(parent_node, children)
					break

			if not found:
				return

		if current_node:
			self.dir_tree.selection_set(current_node)
			self.dir_tree.focus(current_node)
			self.dir_tree.see(current_node)


	""" Processing """
	def get_windows_drives(self):
		drives = []
		bitmask = ctypes.windll.kernel32.GetLogicalDrives()
		for letter in string.ascii_uppercase:
			if bitmask & 1:
				drives.append(f"{letter}:\\")
			bitmask >>= 1
		return drives


	""" Button commands """
	def _command_back_button(self):

		# Back to media file location
		self.app.show_frame('LocateFiles')

	def _command_next_button(self):

		# Forwarding to inspection frame
		self.app.render_new_frame(Inspection, 'Inspection', reinit=True)

	def _command_safe_button(self):

		# Load target drive from metadata
		target_drive = self.app.get_metadata('target_drive')

		# If nothing selected, stop processing
		if not target_drive:
			return

		# Update <<safe_btn>> button
		self.safe_btn.disable()

		# Update settings
		self.user.update_settings(key = 'PATH_TO_MAIN_DRIVE', val = target_drive)

		# Check settings
		if self.user.load_setting_value(key='PATH_TO_MAIN_DRIVE') == target_drive:

			# Update default destination manually
			self.default_destination = target_drive
			self._update_default_destination_text()
			self.safe_btn.set_text('Saved! ✓')


	""" Events """
	def _event_select_item_in_list(self, event):

		target_drive = None
		selected = self.dir_tree.selection()
		if selected:
			node_id = selected[0]
			target_drive = self.dir_tree.item(node_id, 'values')[0] if self.dir_tree.item(node_id, 'values') else self.dir_tree.item(node_id, 'text')
			target_drive = os.path.normpath(target_drive)

		# Check if sth. selected
		if not target_drive:
			return

		# If we have a default destination and it does not match selected drive - enable button and allow saving
		if self.default_destination and self.default_destination != target_drive:
			self.safe_btn.set_text('Save as new default')
			self.safe_btn.enable()
		else:
			self.safe_btn.disable()

		# Update metadata and refresh text
		self.app.set_metadata('target_drive', target_drive)
		self._update_target_drive_text()

	def _on_hover(self, event):
		rowID = self.dir_tree.identify_row(event.y)
		if rowID != self._dir_tree_hover_rowID:
			if self._dir_tree_hover_rowID:
				self.dir_tree.item(self._dir_tree_hover_rowID, tags=('normal',))

			self._dir_tree_hover_rowID = rowID
			if rowID:
				self.dir_tree.item(rowID, tags=('hover',))

	def _on_open(self, event):
		"""Populate subfolders when a node is expanded."""
		item = self.dir_tree.focus()
		children = self.dir_tree.get_children(item)
		# if first child is a dummy, remove it and populate real children
		if children and self.dir_tree.item(children[0], "text") == "":
			self.dir_tree.delete(children[0])
			path = self.dir_tree.item(item, "values")[0]
			self._insert_subfolders(self.dir_tree, item, path)

	def _insert_subfolders(self, tree, parent, path):
		"""Insert subfolders of `path` under parent node."""
		try:
			for name in os.listdir(path):
				full_path = os.path.join(path, name)
				if os.path.isdir(full_path):
					file_count = sum(1 for f in os.scandir(full_path) if f.is_file())
					node = tree.insert(parent, "end", text=name, values=(full_path,file_count,))
					# insert a dummy child to show expand arrow
					tree.insert(node, "end")
		except PermissionError:
			pass  # skip folders without permission