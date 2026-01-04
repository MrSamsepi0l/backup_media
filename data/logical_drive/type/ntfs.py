import os
from core.helper import Helper as h
from core.setup.setup import setup

class NTFS:

	# File type | extensions allowed to copy
	ALLOWED_FILE_TYPE = {
		'image_type'            : ['JPG-Datei', 'JPEG-Datei', 'PNG-Datei'],
		'video_type'            : ['MP4-Datei'],
		'image_extension'       : ['.jpg', '.jpeg', '.png', '.webp', '.gif'],
		'video_extension'       : ['.mp4'],
	}

	def __init__(self, name, mount_path, disk_usage):
		self.name = name
		self.device = 'Unknown'
		self.mount_path = mount_path
		self.disk_usage = disk_usage
		self.fstype = 'NTFS'

	def get_disk_usage(self) -> dict:
		return {
			'total' : self.disk_usage[0],
			'used'  : self.disk_usage[1],
			'free'  : self.disk_usage[2],
			'perc'  : self.disk_usage[3],
		}

	def identify_media_file_locations(self, frame = None):

		# If window-specific options given
		if frame and setup.get_program_mode() == 'window':
			self.frame = frame

		if not os.path.exists(self.mount_path):
			return None

		allowed_ext = tuple(ext.lower() for key in ('image_extension', 'video_extension') for ext in self.ALLOWED_FILE_TYPE[key])
		files_found = 0
		folder_found = 0
		subfolder_count = sum(len(dirs) for _, dirs, _ in os.walk(self.mount_path))

		# Run complete media source path
		for idx, (root, _, files) in enumerate(os.walk(self.mount_path), start=1):

			# Update GUI progress bar
			if setup.get_program_mode() == 'window':

				percent = int(idx / subfolder_count * 100)
				self.frame.progressbar.update_progress(text=root, percent = percent)

				self.frame.progressbar.add_title_text(text='Searching for media files in: ', clear=True)
				self.frame.progressbar.add_title_text_highlighted(text=root, type='default', render=True)

			allowed_files = [f for f in files if f.lower().endswith(allowed_ext)]

			if allowed_files:
				files_found += len(allowed_files)
				folder_found += 1


		self.frame.folder_found = folder_found
		self.frame.files_found = files_found

		return self.mount_path