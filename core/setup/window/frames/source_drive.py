import os, sys
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from data.drive import Drive
from core.setup.design import WindowDesign as Design
from .locate_files import LocateFiles
from .models.buttons.primary import PrimaryButton

@dataclass
class Layout():
	header_row			= 0
	header_row_title 	= 0

	body_row			= 1
	body_row_dir_tree 	= 0

	footer_row 			= 2
	footer_row_buttons 	= 0

class SourceDrive(ttk.Frame):

	def __init__(self, root_frame):
		super().__init__(root_frame)

		# System
		self.app 					= self.winfo_toplevel()
		self.root_frame 			= root_frame
		self.drive 					= None

		# Frames / Views
		self.header 				= None
		self.body 					= None
		self.footer 				= None
		self.button_frame 			= None
		self._button_index 			= 0
		self.dir_tree 				= None

		# Drive chosen by user in directory list (will be set through event by clicking on list-item)
		self.selected_drive 		= None
		self._dir_tree_hover_row 	= None

		# Draw UI
		self.render_UI()

	def render_UI(self):

		# Render header, expanding x-axis, non-expanding y-axis
		self.header = ttk.Frame(self)
		self.grid_columnconfigure(Layout.header_row, weight=1)
		self.header.grid(row=Layout.header_row, column=0, sticky='nsew')
		self.header.grid_columnconfigure(0, weight=1)
		ttk.Label(
			self.header,
			text='Choose drive/device where to copy media files from',
			font=(None, 10, 'bold'),
			padding=(10,5)).grid(row=Layout.header_row_title, column=0, sticky='w')

		# Render body, expanding x-axis, large expanding y-axis
		self.body = ttk.Frame(self)
		self.grid_rowconfigure(Layout.body_row, weight=15)
		self.body.grid(row=Layout.body_row, column=0, sticky='nsew')
		self.body.grid_columnconfigure(0, weight=1)
		self.body.grid_rowconfigure(Layout.body_row, weight=1)

		# Render footer, expanding x-axis, expanding y-axis
		self.footer = ttk.Frame(self)
		self.grid_rowconfigure(Layout.footer_row, weight=1)
		self.footer.grid(row=Layout.footer_row, column=0, sticky='nsew')
		self.footer.grid_columnconfigure(0, weight=1)
		self.footer.grid_rowconfigure(Layout.footer_row, weight=1)

		# Init directory list frame
		self.render_directory_list()

		# Create buttons
		self._render_button('back_btn', PrimaryButton, text='Back', state='normal', command=self._command_back_button)
		self._render_button('next_btn', PrimaryButton, text='Next', state='disabled', command=self._command_next_button)

	def render_directory_list(self):

		def _on_hover(event):
			rowID = self.dir_tree.identify_row(event.y)
			if rowID != self._dir_tree_hover_row:
				if self._dir_tree_hover_row:
					self.dir_tree.item(self._dir_tree_hover_row, tags=('normal',))

				self._dir_tree_hover_row = rowID
				if rowID:
					self.dir_tree.item(rowID, tags=('hover',))


		style = ttk.Style()
		style.configure('Dark.Treeview', background=Design.source_dir_tree.get('main_bg'), foreground='white', fieldbackground=Design.source_dir_tree.get('main_bg'), rowheight=24, borderwidth=0)
		style.map('Dark.Treeview', background=[ ('selected', Design.source_dir_tree.get('select_bg')) ]) # #3A2F3A

		# Updated list
		tree_frame = ttk.Frame(self.body, padding=10)
		tree_frame.grid(row=Layout.body_row_dir_tree, column=0, sticky='nsew')
		tree_frame.grid_rowconfigure(Layout.body_row_dir_tree, weight=1)
		tree_frame.grid_columnconfigure(0, weight=1)

		# Tree view (modern list)
		self.dir_tree = ttk.Treeview(tree_frame, columns='Drive', show='tree', height=8, style='Dark.Treeview', selectmode='browse')
		self.dir_tree.grid(row=0, column=0, sticky='nsew')
		self.dir_tree.tag_configure("hover", background=Design.source_dir_tree.get('hover_bg'))  # hover row
		self.dir_tree.tag_configure("normal", background=Design.source_dir_tree.get('main_bg'))  # normal row

		scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.dir_tree.yview)
		scrollbar.grid(row=0, column=1, sticky="ns")

		self.dir_tree.configure(yscrollcommand=scrollbar.set)
		self.dir_tree.bind('<<TreeviewSelect>>', self.__event_select_item_in_list)	# Select
		self.dir_tree.bind("<Motion>", _on_hover)									# Hover

		# Load directories into list
		self.drive = Drive()
		drive_list = self.drive.get_connected_drives()

		# Clear + insert
		for item in self.dir_tree.get_children():
			self.dir_tree.delete(item)

		for drive in drive_list:
			self.dir_tree.insert("", "end", text=str(drive))

	def _render_button(self, key, Button, text, state, command):

		# Create single button frame
		if not self.button_frame:
			self.button_frame = ttk.Frame(self.footer)
			self.button_frame.grid(row=Layout.footer_row_buttons, column=0, sticky='se')
			# self.button_frame.grid_columnconfigure(0, weight=1) # left spacer expanding

		# Add button to existing frame
		btn = Button(self.button_frame, text=text, state=state, command = command)
		setattr(self, key, btn)

		btn.grid(row=0, column=self._button_index, padx=5, pady=5)
		self._button_index += 1


	""" Button commands """
	def _command_back_button(self):

		# Back to root frame
		self.app.show_frame('RootFrame')

	def _command_next_button(self):

		# If button is disabled, do nothing
		if self.next_btn.is_disabled():
			return

		# But if still no drive selected, do nothing
		if not self.app.get_metadata('selected_drive'):
			return

		# Init new frame
		self.app.render_new_frame(LocateFiles, name = 'LocateFiles', reinit=True)


	""" Events """
	def __event_select_item_in_list(self, event):

		# Check if sth. selected
		has_selected = self.dir_tree.selection()
		if not has_selected:
			return

		# Get selection from list
		selection = self.dir_tree.item(has_selected[0], 'text')

		# On success: returns drive-type object instance
		selected_drive = self.drive.identify_drive(selection)
		if not selected_drive:
			return

		# Safe selected drive in root metadata
		self.app.set_metadata('selected_drive', selected_drive)

		# Enable >>next<< button
		self.next_btn.enable()


