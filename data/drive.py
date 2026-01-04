import os
import psutil
import win32api
import win32com.client
from core.console.console import open_cmd_select_menu
from data.logical_drive.type import NTFS
from data.logical_drive.type import MTP

class Drive:

	DEVICE_FILESYSTEM_LIST = [

		{'name': 'Lokaler Datenträger',  'type': 'Lokaler Datenträger',   'filesystem': 'FIXED'},
		{'name': 'Mobiltelefon',         'type': 'Mobiltelefon',          'filesystem': 'MTP'},
		{'name': 'Digitalkamera',        'type': 'Digitalkamera',         'filesystem': 'MTP'},

	]

	def __init__(self):
		pass

	def choose_drive_user(self, options):
		return open_cmd_select_menu(options)


	def get_connected_drives(self):
		"""
		Uses PowerShell command to create a list of
		partitions, mounts, connected devices on this PC.
		"""

		# Init powershell command
		shell = win32com.client.Dispatch("Shell.Application")
		namespace = shell.Namespace(17) # 17 = "Dieser PC"

		device_list = []
		for device in namespace.Items():

			# If folder and not base system path (C:)
			if device.IsFolder and ('::' in str(device.Path) or not str(device.Path).startswith('C:')):

				# Add device to list
				device_list.append(device)

		# Return list of devices
		return device_list

	def identify_drive(self, drive):

		# Load internal and external list of drives
		drive_list = self.get_drive_list()

		# print(f'DRIVE: {drive}')

		# If drive is string
		if type(drive) is str:

			# for d in drive_list:
			# 	print(d.name)

			drive_list = [d for d in drive_list if d.name in drive or d.name in drive]

		else:

			# Check given device path and name against list of found drive names
			drive_list = [d for d in drive_list if drive.Path in d.name or drive.Name in d.name]

		# Return first found drive or nothing
		return drive_list[0] if drive_list else None

	def get_drive_list(self):

		# Collect internal and external drive objects in lists
		int_drive_list = self.get_internal_drive_list()
		ext_drive_list = self.get_external_drive_list()

		# Merge lists and return them
		return ext_drive_list + int_drive_list

	def _get_volume_name(self, drive):

		try:
			label, serial, _, _, _ = win32api.GetVolumeInformation(drive)
			return label
		except Exception:
			return 'Unknown'

	def get_internal_drive_list(self):

		# Default
		accessable_drives = []

		# If set to false (excludes network drives e.g.)
		include_all_drives = False

		# Check all connected drives
		for partition in psutil.disk_partitions(all=include_all_drives):

			# If not accessable, skip
			if not os.path.exists(partition.device):
				continue

			# Skip unnecessary partitions
			if 'cdrom' in partition.opts:
				continue

			# Use timeout for potentially slow operations

			# Get disk usage
			disk_usage = psutil.disk_usage(partition.device)

			# Default drive
			drive = None

			volume_name = self._get_volume_name(partition.device)

			# print(f'DEVICE: {partition.device}')
			# print(f'MOUNTPOINT: {partition.mountpoint}')

			# For NTFS filesystems
			if partition.fstype == 'NTFS':
				try:
					drive = NTFS(volume_name, partition.mountpoint, disk_usage)
				except Exception as e:
					continue

			# If no drive found, skip
			if not drive:
				continue

			# Append associated drive to list
			accessable_drives.append(drive)

		# Return collected list
		return accessable_drives

	def get_external_drive_list(self):

		# Default
		accessable_drives = []

		# Init powershell
		shell = win32com.client.Dispatch('Shell.Application')
		namespace = shell.namespace(17) # Dieser PC

		# Access namespace items
		for item in namespace.Items():

			# Skip real drives having drive letters
			if ':' in item.Name:
				continue

			# Get non-system-accessable drives only
			if os.path.exists(item.Path):
				continue

			# If not even folder, skip
			if not item.IsFolder:
				continue

			# Create MTP device
			drive = MTP(item, shell)

			# Add instance to list
			accessable_drives.append(drive)

		# Return collected list
		return accessable_drives

