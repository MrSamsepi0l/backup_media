import os
import inspect
import zipfile
from pathlib import Path
from dotenv import load_dotenv
from .log import Log
from alive_progress import alive_bar


class Helper:

	@staticmethod
	def get_base_path():

		# Load root path from environment
		load_dotenv()
		root_path = Path(os.getenv('ROOT_PATH'))

		# If found and path exists, return it
		if root_path and os.path.exists(root_path):
			root_path

		# Fallback (Reminder being careful with this - this is dependent of the location of this file while hardcoded parents given)
		return Path(__file__).resolve().parent.parent

	@staticmethod
	def safe_load_image(full_path, max_image_pixels=None):

		# Import modules
		from PIL import Image, UnidentifiedImageError

		#
		Image.MAX_IMAGE_PIXELS = max_image_pixels

		# Use pillow default
		try:
			return Image.open(full_path)
		except UnidentifiedImageError:
			pass

		# HEIC fallback
		try:
			import pillow_heif
			pillow_heif.register_heif_opener
			return Image.open(full_path)
		except Exception:
			pass

		# RAW fallback
		try:
			import imageio
			img = imageio.imread(full_path)
			return Image.fromarray(img)
		except Exception:
			pass

		# Fallback
		return None

	@staticmethod
	def render_placeholder(template: str, **values) -> str:
		return template.format(**values)

	@staticmethod
	def log(text):

		# Get frame of parent file, extracting filename and line number
		frame = inspect.currentframe().f_back
		filename = frame.f_code.co_filename
		line_number = frame.f_lineno

		# Split complete path to filename and take last 4 subpaths
		parts = os.path.normpath(filename).split(os.sep)
		file = os.sep.join(parts[-4:])

		# Print debug line
		print(f'{Log.error('DEBUG in')} {Log.info('['+file+']')} Line {Log.warning(line_number)}: {Log.bold(text)}')

	@staticmethod
	def mkdir(dir: str) -> bool:

		# Check if dir already exists - return true if so
		if os.path.exists(dir) and os.path.isdir(dir):
			return True

		# Create it and check again - return true if found
		os.makedirs(dir, exist_ok=True)
		if os.path.exists(dir) and os.path.isdir(dir):
			return True

		# Return false in every other case
		return False

	@staticmethod
	def compare_dictionaries(source, destination):
		"""
		Compares two dictionaries with each other creating two
		dictionaries containing unique items and duplicates.
		"""
		unique = {}
		duplicates = {}

		# Save unique and duplicate files
		for key, val in source.items():
			dest_val = destination.get(key)
			if dest_val is None:
				unique[key] = val
			else:
				duplicates[val] = dest_val

		return unique, duplicates

	@staticmethod
	def create_zip(folder_to_zip: str, save_target: str, filename: str) -> bool:

		# TODO: improve structure and error checking

		zip_filename = os.path.join(save_target, filename + ".zip")
		total_files = sum(len(files) for _, _, files in os.walk(folder_to_zip))

		# Copy each duplicate media to duplicate folder
		folder_path = Path(folder_to_zip)
		all_files = list(folder_path.rglob('*'))  # Get all files recursively at once
		file_list = [f for f in all_files if f.is_file()]  # Filter only files
		total_files = len(file_list)

		# Init progress for creating zip file
		with alive_bar(total=total_files, bar="brackets", title=f"Creating .zip file: {Log.info(zip_filename)}", length=60, dual_line=True) as progress:
			with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
				for file_path in file_list:
					arcname = file_path.relative_to(folder_path)

					try:
						zipf.write(file_path, arcname)
					except PermissionError:
						print(f'Permission denied for file: {file_path}')
						progress()
						return False
					finally:
						progress()

		return True

	@staticmethod
	def lower_no_whitespace(s: str):
		"""
		Returns given string in lowercase without complete whitespace.
		"""
		return "".join(s.split()).lower()

	@staticmethod
	def normalize_path(path: str):
		path = os.path.expanduser(path)
		path = os.path.normpath(path)
		return path

	@staticmethod
	def count_files(path_to_files, allowed_extensions = []) -> int:
		"""
		Counts and returns all allowed, found files in given path.
		"""
		total = 0

		# If path not a directory, return here
		if not os.path.isdir(path_to_files):
			return total

		# If allowed extension list given
		if allowed_extensions:

			# Count total number of media files in given folder
			for _, _, files in os.walk(path_to_files):
				total += sum(1 for f in files if os.path.splitext(f.lower())[1] in allowed_extensions)

		else:
			# Count total number of media files in given folder
			for _, _, files in os.walk(path_to_files):
				total += sum(1 for f in files)

		return total

	@staticmethod
	def get_from_dict(d: dict, keys = [], default=None):

		# If string, try to split at dots and create nested list
		if isinstance(keys, str):
			keys = keys.split('.')

		# Run all keys in list and try to get value
		for key in keys:
			if isinstance(d, dict):
				d = d.get(key, default)
			else:
				return default
		return d
