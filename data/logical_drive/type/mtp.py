import os
import shutil
import tempfile
from core.setup.setup import setup
from data.colors import Colors
from alive_progress import alive_it

class MTP:

	FILESYSTEM_STRUCTURE = {
		"Phone Camera"          : ["Interner Speicher", "DCIM", "Camera"],
		"Phone Screenshots"     : ["Interner Speicher", "DCIM", "Screenshots"],
		"WhatsApp Images"       : ["Interner Speicher", "Android", "media", "com.whatsapp", "WhatsApp", "Media", "WhatsApp Images"],
		"WhatsApp Images Sent"  : ["Interner Speicher", "Android", "media", "com.whatsapp", "WhatsApp", "Media", "WhatsApp Images", "Sent"],
		"WhatsApp Videos"       : ["Interner Speicher", "Android", "media", "com.whatsapp", "WhatsApp", "Media", "WhatsApp Video"],
		"WhatsApp Videos Sent"  : ["Interner Speicher", "Android", "media", "com.whatsapp", "WhatsApp", "Media", "WhatsApp Video", "Sent"],
	}

	# File type | extensions allowed to copy
	ALLOWED_FILE_TYPE = {
		"image_type"            : ['JPG-Datei', 'JPEG-Datei', 'PNG-Datei'],
		"video_type"            : ['MP4-Datei'],
		"image_extension"       : ['.jpg', '.jpeg', '.png', '.webp', '.gif'],
		"video_extension"       : ['.mp4'],
	}

	UNALLOWED_FILE_EXPLICIT = {
		"type"                  : ['NOMEDIA-Datei'],
	}

	def __init__(self, drive, shell):
		self.drive = drive
		self.name = drive.Name
		self.device = drive.Type
		self.shell = shell
		self.fstype = 'MTP'

	def get_disk_usage(self) -> dict:
		return {}

	def get_temp_dir(self) -> dict:
		return self.temp_dir

	def set_temp_dir(self, temp_dir = None, temp_folder = None, create_dir=False):

		# If directory not already existing
		if not os.path.exists(temp_folder):

			# If it should be created, do it here
			if create_dir:
				os.makedirs(temp_folder, exist_ok=True)

			# Otherwise return nothing
			else:
				return None

		# Set global
		self.temp_dir = {'dir': temp_dir, 'path': temp_folder}

	def create_temp_dir(self):
		temp_folder = tempfile.mkdtemp(prefix='device_backup_copy_')
		temp_dir = self.shell.namespace(temp_folder)
		self.set_temp_dir(temp_dir, temp_folder)

	def delete_temp_dir(self):

		# Load temp dir and remove with all it's content if existing
		temp_dir = self.get_temp_dir()
		if os.path.exists(temp_dir['path']) and os.path.isdir(temp_dir['path']):
			shutil.rmtree(temp_dir['path'])

	def run_through_filesystem(self, device_item):

		# Helper
		def is_file(item):
			return not item.IsFolder

		def is_folder(item):
			return item.IsFolder

		def safe_get_folder(item, retry = 0, max_retry = 3):

			# Verify retries
			if(retry > max_retry):
				return None
			try:
				folder = item.GetFolder
				return folder if folder else None

			# MTP randomly can throw COM errors (retry recursively)
			except Exception:
				retry += 1
				return safe_get_folder(item, retry)

		def search_folder_on_device(path_list):

			folder = self.drive
			for name in path_list:

				# Load folder
				parent = safe_get_folder(folder)

				# Use next() with generator expression - stops at first match
				folder = next(
					(child for child in parent.Items()
					if is_folder(child) and child.name == name),
					None
				)

				# Handle case where folder wasn't found
				if folder is None:
					return None

			return folder

		# Open device folder
		folder = safe_get_folder(device_item)
		if not folder:
			return None

		# Get temp dir
		temp_dir = self.get_temp_dir()

		files_found = 0
		folder_found = 0

		# Run through predefined filesystem hierarchy
		for name, path_list in self.FILESYSTEM_STRUCTURE.items():

			# Search folder on device using structure path list
			folder = search_folder_on_device(path_list)
			if not folder:
				continue

			# Count
			folder_found += 1

			# Open the found folder
			found_folder = self.shell.namespace(folder)

			if setup.get_program_mode() == 'window':
				folder_item_list = found_folder.Items()
				total_items = len(list(folder_item_list)) or 1
				self.frame.progressbar.add_title_text(text='Searching media files in: ', clear=True)
				self.frame.progressbar.add_title_text_highlighted(text=name, type='default', render=True)

			else:
				folder_item_list = alive_it(found_folder.Items(), bar="brackets", title=f'Collecting media files from: {Colors.PRIMARY}{name}{Colors.RESET}', length=40, dual_line=True)

			# Init progress bar list
			for i, folder_item in enumerate(folder_item_list, start = 1):

				# Skip folders
				if is_folder(folder_item):
					continue

				# If it's a file
				elif is_file(folder_item):

					# Window-mode
					if setup.get_program_mode() == 'window':
						percent = int(i / total_items * 100)
						self.frame.progressbar.update_progress(text=folder_item, percent = percent)

					# Update progress (folder_item_list is also progress-bar object in console mode)
					if setup.get_program_mode() == 'console':
						folder_item_list.text(f'Processing file: {Colors.PROCESS}{folder_item}...{Colors.RESET}')

					files_found += 1

					# Check if file is allowed
					if not self.is_file_allowed(folder_item):
						continue

					# Init shell (Important: explicitly reinit on every loop for not "losing connection" to filesystem)
					shell_destination = self.shell.namespace(temp_dir['dir'])

					# Copy file
					shell_destination.CopyHere(folder_item, 20) # 16 = no UI, 4 = ignore

		# Status update for windowed mode
		if(setup.get_program_mode() == 'window'):
			self.frame.folder_found = folder_found
			self.frame.files_found = files_found

		else:
			print(f'\nFound {Colors.SUCCESS}{folder_found}{Colors.RESET} folder(s) including {Colors.SUCCESS}{files_found}{Colors.RESET} file(s).')

	def is_file_allowed(self, shell_file):

		# Skip if file matches explicitly excluded one
		if shell_file.Type in self.UNALLOWED_FILE_EXPLICIT['type']:
			return False

		# If file has an extension
		split = os.path.splitext(shell_file.Name)
		ext = split[1] if split[1] else None

		# If we have a extension and it's not allowed (but it could be missing - depending on OS setting)
		if ext and ext not in self.ALLOWED_FILE_TYPE['image_extension'] and ext not in self.ALLOWED_FILE_TYPE['video_extension']:
			return False

		# Allow by default
		return True

	def identify_media_file_locations(self, frame = None):

		# Load list of file locations potentially containing media files, create temporary files and and create dictionary of files including information about it

		# If window-specific options given
		if frame and setup.get_program_mode() == 'window':
			self.frame = frame

		# Get drive
		drive = self.drive

		# If parent main is not even a folder
		if not drive.IsFolder:
			return

		# Create temporary folder
		self.create_temp_dir()

		# Init process
		self.run_through_filesystem(drive)

		# Get temporary folder
		temp_dir = self.get_temp_dir()

		return temp_dir['path']