import os
import ctypes
from core import Helper as h
from dotenv import load_dotenv
from dataclasses import dataclass
from .console.windows_path_completer import WindowsPathCompleter

@dataclass
class Config():

	PROGRAM_MODES = { 'console', 'window' }

	def __init__(self, program_mode: str = 'console'):
		self.set_program_mode(program_mode)

	def get_program_mode(self) -> str:
		return self.program_mode

	def set_program_mode(self, program_mode: str) -> None:
		if program_mode not in self.PROGRAM_MODES:
			raise ValueError(f'Invalid program mode: {program_mode}', f'Allowed: {', '.join(self.PROGRAM_MODES)}')
		self.program_mode = program_mode

	def get_program_title(self) -> str:
		return self.program_title

	def set_program_title(self, program_title: str) -> None:
		self.program_title = program_title

class Setup:

	def __init__(self):
		""" Sets some configurations at beginning of main program running process. """

		# Load program mode from environment
		load_dotenv()
		program_mode = os.getenv('PROGRAM_MODE')
		program_title = os.getenv('PROGRAM_TITLE') or None

		# Init config
		self.config = Config(program_mode)
		if program_title:
			self.config.set_program_title(program_title)

		# Run method based on program mode
		run_method = 'init_' + str(program_mode)
		if not callable(getattr(self, run_method)):
			raise Exception(f'Failed to setup. Can not call "run_method": {run_method} for "program_mode": {program_mode}')
		getattr(self, run_method)()

	def init_console(self):

		# Enable ANSI for Windows CMD
		self.enable_windows_ansi()

		# Init path completion
		WPC = WindowsPathCompleter()
		WPC.setup_autocomplete(show_hidden=True)

	def init_window(self):
		pass

	def get_program_mode(self):

		# Return capsuled call result
		return self.config.get_program_mode()

	def get_program_title(self):

		# Return capsuled call result
		return self.config.get_program_title()

	def enable_windows_ansi(self):
		"""
		Enables ANSI escape codes for Windows CMD / PowerShell.
		Safe on Linux/Mac (does nothing).
		"""
		if os.name != "nt":
			return True

		kernel32 = ctypes.windll.kernel32
		handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11

		mode = ctypes.c_uint()
		if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
			return False

		# Enable VT100 escape sequences
		ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
		new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING

		return kernel32.SetConsoleMode(handle, new_mode) != 0

# Create single setup instance
setup = Setup()