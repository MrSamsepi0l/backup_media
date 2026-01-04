import os
import glob
import readline

class WindowsPathCompleter:
	"""
	Path autocompletion for Windows console with proper handling of:
	- Drive letters (C:, D:, etc.)
	- Backslashes and forward slashes
	- UNC paths (\\server\\share)
	- Hidden files and folders
	- Case-insensitive matching
	"""

	def __init__(self, show_hidden=True):
		self.show_hidden = show_hidden
		self.matches = []

	def complete(self, text, state):
		"""Main completion function called by readline"""
		if state == 0:
			# First call - generate all matches
			self.matches = self._get_matches(text)

		# Return match for current state
		try:
			return self.matches[state]
		except IndexError:
			return None

	def _get_matches(self, text):
		"""Generate list of path matches"""
		try:
			# Expand user home and environment variables
			text = os.path.expandvars(os.path.expanduser(text))

			# Handle empty input - show current directory
			if not text:
				text = '.\\'

			# Normalize path separators for Windows
			text = text.replace('/', '\\')

			# Handle drive letter completion (C:, D:, etc.)
			if len(text) == 2 and text[1] == ':':
				return self._complete_drive(text)

			# Handle UNC paths (\\server\share)
			if text.startswith('\\\\'):
				return self._complete_unc(text)

			# Regular path completion
			return self._complete_path(text)

		except Exception as e:
			# Return empty list on any error
			return []

	def _complete_drive(self, text):
		"""Complete drive letters (C:, D:, etc.)"""
		drive = text[0].upper()

		# Check if drive exists
		if os.path.exists(f"{drive}:\\"):
			# Show root of drive
			try:
				entries = os.listdir(f"{drive}:\\")
				matches = [f"{drive}:\\{entry}" for entry in entries]
				return self._format_matches(matches)
			except (PermissionError, OSError):
				return [f"{drive}:\\"]

		return []

	def _complete_unc(self, text):
		"""Complete UNC paths (\\server\\share)"""
		# Use glob for UNC path completion
		pattern = text + '*'
		matches = glob.glob(pattern)
		return self._format_matches(matches)

	def _complete_path(self, text):
		"""Complete regular paths"""
		# Split into directory and filename parts
		if text.endswith('\\'):
			# Completing within a directory
			dirname = text
			basename = ''
		else:
			dirname, basename = os.path.split(text)
			if not dirname:
				dirname = '.'

		# Expand dirname
		dirname = os.path.expanduser(dirname) if dirname else '.'

		try:
			# Check if directory exists
			if not os.path.isdir(dirname):
				# Try glob pattern matching
				pattern = text + '*'
				matches = glob.glob(pattern)
				return self._format_matches(matches)

			# List directory contents
			entries = os.listdir(dirname)

			# Filter by basename (case-insensitive for Windows)
			basename_lower = basename.lower()
			matches = [
				os.path.join(dirname, entry)
				for entry in entries
				if entry.lower().startswith(basename_lower)
			]

			# Filter hidden files if needed
			if not self.show_hidden:
				matches = [m for m in matches if not self._is_hidden(m)]

			return self._format_matches(matches)

		except (PermissionError, OSError):
			return []

	def _format_matches(self, matches):
		"""Format matches with trailing backslash for directories"""
		formatted = []
		for match in matches:
			try:
				if os.path.isdir(match) and not match.endswith('\\'):
					formatted.append(match + '\\')
				else:
					formatted.append(match)
			except (PermissionError, OSError):
				formatted.append(match)

		# Sort: directories first, then files (case-insensitive)
		formatted.sort(key=lambda x: (not x.endswith('\\'), x.lower()))

		return formatted

	def _is_hidden(self, path):
		"""Check if file/folder is hidden on Windows"""
		try:
			import ctypes
			attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
			return attrs != -1 and bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN
		except:
			# Fallback: check if starts with dot
			return os.path.basename(path).startswith('.')


	def setup_autocomplete(self, show_hidden=True):
		"""
		Setup path autocompletion for Windows console

		Args:
			show_hidden: Whether to show hidden files/folders in completion
		"""
		self.show_hidden = show_hidden
		readline.set_completer(self.complete)

		# Set delimiter to split only on spaces and tabs
		readline.set_completer_delims('\t\n')

		# Enable tab completion
		readline.parse_and_bind('tab: complete')

		# Show all matches if multiple completions available
		readline.parse_and_bind('set show-all-if-ambiguous on')

		# Show common prefix before showing all matches
		readline.parse_and_bind('set completion-prefix-display-length 2')