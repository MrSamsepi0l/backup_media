import os
from core.log import Log

class UserInput:

	KEYS = {

		"MAIN_DRIVE"        : "PATH_TO_MAIN_DRIVE",             # where the existing medias are saved - main image storage for comparison of uniques
		"BACKUP_DRIVE"      : "PATH_TO_BACKUP_DRIVE",           # most likely other partition used as backup - this drive will be synced from the main drive
		"ZIP_DRIVE"			: "PATH_TO_BACKUP_ZIP",
		"ZIP_FILENAME"		: "BACKUP_ZIP_FILENAME"

	}

	def __init__(self, user):
		self.user = user


	def _get_key(self, key):
		return self.KEYS.get(key)

	def get_destination_drive(self):

		# Drive where images should be copied to (and existing images lying) - load default from JSON
		default_destination = self.user.load_setting_value(key = self._get_key('MAIN_DRIVE'))

		# Take default?
		print()
		print(Log.warning(f'Choose destination where to store media files.'))
		take_default_destination = self.confirm_yes_no(f"Take default destination ({Log.info(default_destination)})?")
		if take_default_destination:
			return default_destination

		# Access perma loop until given destination is valid
		while True:
			destination_path = input(f"Enter path to folder where to copy media files to {Log.info('(like D:\\Bilder)')}: ")

			# If not existing or not a directory
			if not os.path.exists or not os.path.isdir(destination_path):
				print()
				print(f"Please input a valid and existing path to the destination folder.")
				return self.get_destination_drive()

			# Ask if setting update wanted
			update_default_destination = self.confirm_yes_no(f"\nSave selected destination as default? {Log.info('('+destination_path+')')}?")
			if update_default_destination:
				self.user.update_settings(key = self._get_key('MAIN_DRIVE'), val = destination_path)

			return destination_path

	def get_backup_drive(self, retry = 0, max_retry = 5):

		# If max retries reached, stop
		if retry > max_retry:
			return

		# Drive where images should be copied to (and existing images lying) - load default from JSON
		default_backup_drive = self.user.load_setting_value(key = self._get_key('BACKUP_DRIVE'))

		# Take default?
		print()
		print(Log.warning(f'Choose your backup drive.'))
		take_default = self.confirm_yes_no(f"Take default? ({Log.info(default_backup_drive)})?")
		if take_default:
			return default_backup_drive

		# Get path to backup drive
		backup_drive = input(f"Enter path to backup drive e.g.: {Log.info('(E:\\Bilder)')}: ").strip().lower()
		if os.path.exists(backup_drive) and os.path.isdir(backup_drive):

			# Ask if setting update wanted
			update_default_setting = self.confirm_yes_no(f"\nSave selected backup drive as default? {Log.info('('+backup_drive+')')}?")
			if update_default_setting:
				self.user.update_settings(key = self._get_key('BACKUP_DRIVE'), val = backup_drive)

			return backup_drive

		# Retry while allowed
		print(f'Path not existing. {max_retry - retry} retries remaining.')
		return self.get_backup_drive(retry = retry + 1)

	def get_zip_drive(self):

		# Drive where zip of all images should be created (and possible already a .zip file for images existing - or other files)
		default_zip_drive = self.user.load_setting_value(key = self._get_key('ZIP_DRIVE'))

		# Take default?
		print()
		print(Log.warning(f'Choose destination where to store media files.'))
		take_default_zip = self.confirm_yes_no(f"Take default ({Log.info(default_zip_drive)})?")
		if take_default_zip:
			return default_zip_drive

		# Access perma loop until given destination is valid
		while True:
			zip_drive = input(f"Enter path to folder where to save .zip file {Log.info('(like E:\\Bilder)')}: ")

			# If not existing or not a directory
			if not os.path.exists or not os.path.isdir(zip_drive):
				print()
				print(f"Please input a valid and existing path to the destination folder.")
				return self.get_zip_drive()

			# Ask if setting update wanted
			update_default_zip = self.confirm_yes_no(f"\nSave selected destination as default? {Log.info('('+zip_drive+')')}?")
			if update_default_zip:
				self.user.update_settings(key = self._get_key('ZIP_DRIVE'), val = zip_drive)

			return zip_drive

	def get_zip_filename(self):

		# Filename of .zip file
		zip_filename = self.user.load_setting_value(key = "BACKUP_ZIP_FILENAME")
		return zip_filename

	def confirm_yes_no(self, prompt: str, force_yes=False) -> bool:
		"""Creates perma loop to force YES/NO selection"""

		while True:
			# answer = input(f"{prompt} ({Log.success('yes')}/{Log.error('no')}): ").strip().lower()
			answer = input(f"{prompt} (Y/N): ").strip().lower()

			if answer in ["y", "yes", "Y", "YES"]:
				return True
			elif force_yes:
				return self.confirm_yes_no(prompt)
			if answer in ("no"):
				return False
			else:
				return self.confirm_yes_no(prompt)