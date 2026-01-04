import os
import json
from core.helper import Helper as h
from core.log import Log
from config.user.input import UserInput

class User:

	DEFAULT_DATA        = {}

	def __init__(self):
		self.user_input = UserInput(self)
		self.path_to_settings = os.path.join('config', 'user', 'settings.json')


	def get_destination_drive(self):

		# Forward process to user selection
		return self.user_input.get_destination_drive()

	def get_default_destination_drive(self):

		default_destination = self.load_setting_value(key = 'PATH_TO_MAIN_DRIVE')
		return default_destination

	def get_zip_drive(self):

		# Forward process to user selection
		return self.user_input.get_zip_drive()

	def get_zip_filename(self):

		# Forward process to load zip filename
		return self.user_input.get_zip_filename()

	def get_backup_drive(self, retry = 0, max_retry = 5):

		# Forward process to user selection
		return self.user_input.get_backup_drive(retry, max_retry)

	def confirm_yes_no(self, prompt, force_yes=False):

		# Forward process to user confirmation
		return self.user_input.confirm_yes_no(prompt, force_yes)

	def load_settings(self):

		# Check if file exists, create if not
		if not os.path.exists(self.path_to_settings):
			self.create_settings()

		# Load settings
		try:
			with open(self.path_to_settings, "r", encoding="utf-8") as file:
				data = json.load(file)

		except Exception as e:
			Log.error(f'Failed to load user JSON settings with: {e}')
			return None

		# Return settings
		return data

	def load_setting_value(self, key):

		# Load settings
		data = self.load_settings()
		if not data:
			return

		# Return value stored at key - none if missing
		return data.get(key)

	def update_settings(self, key, val):

		# If not existing, create here
		if not os.path.exists(self.path_to_settings):
			self.create_settings()

		# Load settings
		with open(self.path_to_settings, "r+", encoding="utf-8") as file:
			data = json.load(file)
			if not data:
				data = {}

			# Update settings
			data[key] = val
			file.seek(0)
			json.dump(data, file, indent=4)
			file.truncate()

	def create_settings(self):

		# File exists, nothing to do
		if os.path.exists(self.path_to_settings):
			return

		try:
			with open(self.path_to_settings, "w", encoding="utf-8") as file:
				json.dump(self.DEFAULT_DATA, file, indent=4, ensure_ascii=False)

		except Exception as e:
			Log.error(f'Failed to create user JSON settings with: {e}')