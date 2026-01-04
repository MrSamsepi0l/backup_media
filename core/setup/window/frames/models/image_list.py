import os
import queue
import threading
import tkinter as tk
from tkinter import ttk
from .buttons.primary import PrimaryButton
from core.helper import Helper as h
from PIL import Image, ImageTk

class ImageList(ttk.Frame):

	def __init__(self, root_frame, image_size, bg='#f0f0f0'):
		super().__init__(root_frame)

		self.root_frame = root_frame
		self.image_size = image_size
		self.image_frame = None
		self.canvas = None
		self.canvas_window = None
		self.photo_images = []
		self.image_rotations = {}

		# Create queue for processing threads (like loading images async)
		self.image_queue = queue.Queue()

		# Configure this frame's grid
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		# Draw canvas within parent frame
		self.canvas = tk.Canvas(self, bg='#f0f0f0', highlightthickness=0)
		self.h_scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
		self.canvas.configure(xscrollcommand=self.h_scrollbar.set)

		# Grid canvas and scrollbar
		self.canvas.grid(row=0, column=0, sticky='nsew')
		self.h_scrollbar.grid(row=1, column=0, sticky='ew')

		self.image_frame = tk.Frame(self.canvas, bg = bg)
		self.canvas_window = self.canvas.create_window((0, 0), window=self.image_frame, anchor='nw')

	def update_scroll_region(self):
		"""Force update scroll region"""
		self.image_frame.update_idletasks()
		self.canvas.update_idletasks()
		bbox = self.canvas.bbox('all')
		self.canvas.configure(scrollregion=bbox)

	def _load_image_async(self, sorted_list):

		# Open thread
		threading.Thread(target=self._image_loader_thread, args=(sorted_list,), daemon=True).start()
		self.after(50, self._process_image_queue)

	def _image_loader_thread(self, sorted_list):

		for idx, (filename, full_path) in enumerate(sorted_list):
			try:

				img = h.safe_load_image(full_path)
				if not img:
					continue
				# img = Image.open(full_path)
				img.thumbnail((self.image_size, self.image_size), Image.Resampling.LANCZOS)

				# Add image copy to queue
				self.image_queue.put((os.path.basename(filename), img.copy(), full_path, idx))

			except Exception as e:
				print(f'Failed loading {full_path}: {e}')

		# Signal finished
		self.image_queue.put(None)

	def _process_image_queue(self):
		try:
			while True:
				item = self.image_queue.get_nowait()
				if item is None:
					self.update_scroll_region()
					return

				filename, pil_img, full_path, idx = item
				self._add_image_ui(filename, pil_img, full_path, idx)

		except queue.Empty:
			self.after(50, self._process_image_queue)

	def _add_image_ui(self, filename, pil_img, full_path, index):

		# Initialize rotation for this image
		if full_path not in self.image_rotations:
			self.image_rotations[full_path] = 0

		photo = ImageTk.PhotoImage(pil_img)
		self.photo_images.append(photo)

		# Apply rotation if any
		if self.image_rotations[full_path] != 0:
			pil_img = pil_img.rotate(-self.image_rotations[full_path], expand=True)

		# Calculate grid position
		row, col = (0, index)

		# Outer container frame - contains image frame AND text label separately
		container = tk.Frame(self.image_frame, bg='#f0f0f0', relief='solid', borderwidth=1, width=self.image_size, height=self.image_size+10)
		container.grid(row=row, column=col, padx=5, pady=5, sticky='n')

		# Configure container grid
		container.grid_rowconfigure(0, weight=0)  # Image row - fixed size
		container.grid_rowconfigure(1, weight=0)  # Text row - fixed size
		container.grid_columnconfigure(0, weight=1)

		# Create frame for image only
		frame = tk.Frame(container, bg='white', width=self.image_size, height=self.image_size)
		frame.grid(row=0, column=0, sticky='n')
		frame.grid_propagate(False)  # Prevent frame from resizing

		# Image label inside image_frame
		label = tk.Label(frame, image=photo, bg='white', cursor='hand2')
		label.grid(row=0, column=0, sticky='nsew')

		# Make image clickable
		label.bind('<Button-1>', lambda e: self._open_image_popup(full_path, filename))

		# Configure image_frame grid
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)

		# Filename label
		name_label = tk.Label(
			container,
			text=filename,
			bg='white',
			font=('Segoe UI', 6),
			wraplength=self.image_size - 20,
		)
		name_label.grid(row=1, column=0, pady=(5, 0), sticky='ew')

		# Button bar (top right corner)
		button_bar = tk.Frame(container, bg='white', relief='solid', borderwidth=1)
		button_bar.place(relx=1.0, rely=0.0, anchor='ne', x=-5, y=5)

		# Rotate button
		rotate_btn = tk.Button(
			button_bar,
			text='↻',
			font=('Segoe UI', 7, 'bold'),
			bg="#152931",
			fg='white',
			activebackground="#274C5A",
			activeforeground='white',
			relief='flat',
			padx=6,
			pady=2,
			cursor='hand2',
			command=lambda p=full_path, fn=filename, idx=index: self._rotate_image(p, fn, idx)
		)
		rotate_btn.pack(side='left', padx=2, pady=2)

	def _open_image_popup(self, full_path, filename):
		import subprocess
		subprocess.run(
			['cmd', '/c', 'start', '', full_path],
			shell=True
		)

	def _rotate_image(self, full_path, filename, index):

		"""Rotate image by 90 degrees"""
		# Update rotation (0, 90, 180, 270, then back to 0)
		self.image_rotations[full_path] = (self.image_rotations[full_path] + 90) % 360

		# Reload the specific image
		self._reload_image(filename, full_path, index)

		print(f"Rotated {filename} to {self.image_rotations[full_path]}°")

	def _reload_image(self, filename, full_path, index):
		"""Reload a specific image after rotation"""
		try:
			# Calculate grid position
			row, col = (0, index)

			# Find and destroy the old container at this position
			for widget in self.image_frame.grid_slaves(row=row, column=col):
				widget.destroy()

			# Load and resize image
			pil_img = Image.open(full_path)

			# Apply rotation if any
			if self.image_rotations[full_path] != 0:
				pil_img = pil_img.rotate(-self.image_rotations[full_path], expand=True)

			pil_img.thumbnail((self.image_size, self.image_size), Image.Resampling.LANCZOS)

			# Re-add the image with new rotation
			self._add_image_ui(filename, pil_img, full_path, index)

		except Exception as e:
			print(f"Error reloading {filename}: {e}")

	def _on_frame_configure(self, event=None):
		"""Update scroll region when frame size changes"""
		self.canvas.configure(scrollregion=self.canvas.bbox('all'))

	def _on_mousewheel(self, event):

		# When using mousewheel/scroll
		self.canvas.xview_scroll(int(-event.delta / 120), 'units')
		return "break"

	def _bind_mousewheel(self, event):

		# Add custom mousewheel event binding
		self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

	def _unbind_mousewheel(self, event):

		# Get current position and position of (hovered) canvas
		x, y = self.canvas.winfo_pointerxy()
		canvas_x = self.canvas.winfo_rootx()
		canvas_y = self.canvas.winfo_rooty()
		canvas_width = self.canvas.winfo_width()
		canvas_height = self.canvas.winfo_height()

		# If still inside canvas - keep binding
		if (canvas_x <= x <= canvas_x + canvas_width and canvas_y <= y <= canvas_y + canvas_height):
			return

		# Actually leaving - unbind
		self.canvas.unbind_all('<MouseWheel>')