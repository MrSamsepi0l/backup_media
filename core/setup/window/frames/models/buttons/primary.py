from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

@dataclass
class Button:
	font 			= ('Arial', 10)
	padding 		= (2, 2)
	borderwidth		= 0
	bg_disabled		= '#888888'
	fg_disabled		= '#cccccc'
	fg_text			= '#313131'

class PrimaryButton(ttk.Frame):
	def __init__(self, parent, text='Primary-Button', state=None, command=None, width=None, style_name='Modern.Primary.TButton', **options):
		super().__init__(parent)

		# Create style
		self.style = ttk.Style()

		self.style_config = {
			'style_name' 	: style_name,
			'font' 			: Button.font,
			'padding' 		: Button.padding,
			'foreground' 	: Button.fg_text,
			'borderwidth' 	: Button.borderwidth,
		}

		self.style_config.update(options)

		# Apply config
		self.style.configure(style_name, **self.style_config)
		self.style.map(style_name, background=[('disabled', Button.bg_disabled)], foreground=[('disabled', Button.fg_disabled)])

		# Create button frame
		self.button = ttk.Button(self, text=text, command=command, state=state, style=style_name, width=width)
		self.button.pack(fill='x', expand=True)

	# Allow dynamic button update
	def set_text(self, text: str):
		self.button.config(text=text)

	def set_command(self, command: function):
		self.button.config(command=command)

	def get_state(self):
		return self.button.state()

	def is_disabled(self):
		return 'disabled' == self.get_state()[0]

	def enable(self):
		self.set_state('!disabled')

	def disable(self):
		self.set_state('disabled')

	def set_state(self, state: str):
		self.button.state([state])

	def set_style(self, **kwargs):
		self.style.configure(self.button.cget('style'), **kwargs)

