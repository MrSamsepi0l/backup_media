from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

@dataclass
class Info:
	font 			= ('Arial', 10, 'bold')
	height			= 1
	width			= 80
	borderwidth		= 0
	spacing1		= 5
	spacing3		= 5
	foreground		= '#000000'
	background		= '#F0F0F0'
	justify			= 'center'

class InfoText(ttk.Frame):
	def __init__(self, parent, text='InfoText', high_text=None, high_color = '#4684BB', state='disabled', tag_name='Info.Text'):
		super().__init__(parent)

		self.tag_name = tag_name
		self.high_color = high_color
		self.tag_config = {
			'spacing1' 		: Info.spacing1,
			'spacing3' 		: Info.spacing3,
			'foreground' 	: Info.foreground,
			'background'	: Info.background,
			'justify'		: Info.justify,
		}

		# Create text widget
		self.infotext = tk.Text(self, height=Info.height, width=Info.width, borderwidth=Info.borderwidth, fg=Info.foreground, bg=Info.background)
		self.infotext.pack()

		# Filter empty values and configure tags
		tag_options = {k: v for k, v in self.tag_config.items() if v is not None}
		self.infotext.tag_configure(tag_name, **tag_options)

		# Set font
		self.set_config('font', Info.font)

		# Insert actual text and also add modified highlight text
		self.add_text(text)
		if high_text is not None:
			self.add_text(high_text, 'colored_info')
			self.set_config('foreground', high_color, 'colored_info')

		# Finally set state
		self.set_state(state)


	# Allow dynamic text update
	def set_text(self, text, tag_name = None):
		self.enable()
		self.infotext.delete('1.0', 'end')
		self.add_text(text, tag_name)
		self.disable()

	def set_high_text(self, text, high_text):
		self.enable()
		self.infotext.delete('1.0', 'end')
		self.add_high_text(text, high_text)
		self.disable()

	def add_text(self, text: str, tag_name = None):
		if tag_name:
			self.infotext.insert('end', text, tag_name)
		else:
			self.infotext.insert('end', text)

	def add_high_text(self, text, high_text):
		self.add_text(text)
		self.add_text(high_text, 'colored_info')
		self.set_config('foreground', self.high_color, 'colored_info')

	def get_state(self):
		return self.cget('state')

	def is_disabled(self):
		return self.get_state() == 'disabled'

	def enable(self):
		self.set_state('normal')

	def disable(self):
		self.set_state('disabled')

	def set_state(self, state: str):
		self.infotext.configure(state=state)

	def set_config(self, key, value, tag_name = None):
		if tag_name:
			self.infotext.tag_configure(tag_name, **{key: value})
		else:
			self.infotext.configure(**{key: value})