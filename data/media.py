import os
import magic
import shutil
import unicodedata
from core import Helper as h, Log
from alive_progress import alive_bar

class Media:

	def __init__(self, path: str):
		self.path = path
		self.media_files = {}
		self.duplicate_folder = ''
		self.duplicate_sub_folder_name_source = 'already_existing'
		self.duplicate_sub_folder_name_target = 'media_files_to_copy'
		self.duplicate_folder_name = 'duplicates'
		self.target_save_folder = ''
		self.target_save_folder_name = 'Saved Media Files By Script'
		self.allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".mp4", ".webm", ".mkv", ".avi", ".mov"}

	def _create_duplicate_folder(self) -> tuple:

		# Set default result and duplicate folder (even if folder potentially not existing right now)
		default_result = (None, None, None)
		self.duplicate_folder = os.path.join(self.path, self.duplicate_folder_name)

		# Check if folder existing - otherwise create it
		dir_existing = h.mkdir(self.duplicate_folder)
		if not dir_existing:
			return default_result

		# Helper to create subfolders in recently created parent duplicate folder
		def create_subfolder(subfolder):
			subfolder = os.path.join(self.duplicate_folder, subfolder)
			h.mkdir(subfolder)
			return subfolder

		# Create subfolder (the files coming from the chosen device to copy onto this PC)
		sub_source_folder = create_subfolder(self.duplicate_sub_folder_name_source)
		if not sub_source_folder:
			return default_result

		# Create subfolder (the already existing medias from the selected main drive on this PC)
		sub_target_folder = create_subfolder(self.duplicate_sub_folder_name_target)
		if not sub_target_folder:
			return default_result

		# Return duplicate folder and it's subfolders
		return (self.duplicate_folder, sub_source_folder, sub_target_folder)

	def get_duplicate_folder(self):
		return self.duplicate_folder

	def _create_target_save_folder(self):
		self.target_save_folder = os.path.join(self.path, self.target_save_folder_name)

		# Check if path exists, create dir if wanted and handle error
		if not os.path.exists(self.target_save_folder) or not os.path.isdir(self.target_save_folder):
			os.makedirs(self.target_save_folder, exist_ok=True)

		# TODO: Handle error if path doesn't exist

		return self.target_save_folder

	def get_target_save_folder(self):
		return self.get_target_save_folder()

	def load_media_files(self) -> dict:

		# Default
		media_files = {}

		# If path is invalid
		if not os.path.exists(self.path):
			return media_files

		# Run complete media source path
		for root, _, files in os.walk(self.path):
			for filename in files:

				# Get full path to media
				full_path = os.path.normpath(os.path.join(root, filename))
				if not os.path.exists(full_path):
					continue

				# Skip non-files
				if not os.path.isfile(full_path):
					h.log(f'Is not file: {filename}')
					continue

				# Check if valid media extension
				ext = os.path.splitext(filename)[1].lower()

				# If we have a extension and it doesn't match, skip
				if ext and ext not in self.allowed_extensions:
					continue

				if not ext:

					try:
						with open(full_path, 'rb') as f:
							f.read(1)
						real_path = unicodedata.normalize('NFC', full_path)
						real_path = os.path.realpath(real_path).rstrip('\\/')
						mime = magic.from_file(real_path, mime=True)

					except PermissionError as e:
						pass

					except Exception as e:
						print(f'Magic/Open failed: {repr(full_path)} ({e})')
						continue

					if not mime.startswith(('image/')): # 'video/', 'audio/'
						continue

				# Save to dictionary
				media_files[filename] = full_path

		self.media_files = media_files
		return media_files

	def copy_duplicate_media_files(self, files) -> None:
		"""Copy given files to duplicate folder (including subfolders)
		   at class instance path
		"""

		# Create duplicate folder including subfolders
		(duplicate_folder, sub_source_folder, sub_target_folder)  = self._create_duplicate_folder()
		if not duplicate_folder or not sub_source_folder or not sub_target_folder:
			return

		# Copy each duplicate media to duplicate folder
		with alive_bar(total=len(files.items()), bar="brackets", title=f"Copying duplicate media files to: {Log.info(self.path)}", length=60, dual_line=True) as progress:
			for media_to_copy_full_path, existing_full_path in files.items():

				# Update progress
				progress.text(f'Copying: {Log.process(media_to_copy_full_path)}')

				#print(f'Media existing full path: {existing_full_path}')
				#print(f'Media to copy full path: {media_to_copy_full_path}')

				# Copy existing media into subfolder
				shutil.copy2(existing_full_path, sub_source_folder)

				# Copy media-to-copy into subfolder
				shutil.copy2(media_to_copy_full_path, sub_target_folder)

				progress()

	def copy_unique_media_files(self, unique_media_files: dict):

		# Set folder where fils will be saved (create if not existing)
		target_save_folder = self._create_target_save_folder()
		if not target_save_folder:
			return

		# Init progress for copying files
		with alive_bar(total=len(unique_media_files), bar="brackets", title=f"Copying unique media files to: {Log.info(target_save_folder)}", length=60, dual_line=True) as progress:
			for key, file_path in unique_media_files.items():

				# Copy medias into folder
				shutil.copy2(file_path, target_save_folder)
				progress()

	def delete_duplicate_folder(self):

		# Delete duplicate media folder and all it's content
		duplicate_folder = self.get_duplicate_folder()
		if os.path.exists(duplicate_folder) and os.path.isdir(duplicate_folder):
			shutil.rmtree(duplicate_folder)