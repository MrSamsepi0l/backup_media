import os, sys
from core.setup.setup import setup
from data.drive import Drive
from data.colors import Colors
from data.media import Media
from core import Helper as h, Log, DirectorySynchronizer
from config import User
from core.window import Window

def run_console():

	# Get list of connected devices/drives
	drive = Drive()
	drive_options = drive.get_connected_drives()
	if not drive_options:
		raise Exception("No drive options found.")

	# Let user choose his drive
	selected_drive = drive.choose_drive_user(drive_options)
	if not selected_drive:
		raise Exception(f"No drive selected.")

	# Identify selected drive (and it's filesystem)
	identified_drive = drive.identify_drive(selected_drive)
	if not identified_drive:
		raise Exception(f'Drive {selected_drive.Name} was not identified properly.')

	# TODO Add params to function; maybe what medias are wanted
	path_medias_to_copy = identified_drive.identify_media_file_locations()
	if not path_medias_to_copy:
		e =  f'{Log.error('No media file locations found for drive: ') + Log.info(identified_drive.name) + ' (' + Log.info(identified_drive.fstype + ' filesystem') + ')'}'
		raise Exception(e)

	# Create instance for medias to copy
	medias_to_copy = Media(path = path_medias_to_copy)

	# Init user instance and let user choose destination where to save files
	user = User()
	dest_drive = user.get_destination_drive()
	if not os.path.exists(dest_drive):
		raise Exception(f'Selected destination ({Log.info(dest_drive)}) not existing.')

	# Load medias from destination (the medias that are already existing)
	destination_drive = Media(path = dest_drive)

	# Search for unique and duplicate media files
	unique_medias, duplicate_medias = h.compare_dictionaries(medias_to_copy.load_media_files(), destination_drive.load_media_files())

	print(f"\nUnique medias found to copy:                      {Colors.SUCCESS}{len(unique_medias)}{Colors.RESET}")
	print(f"Duplicate medias found to check individually:   {Colors.SUCCESS}{len(duplicate_medias)}{Colors.RESET}")
	print()

	# Save copies of duplicate medias to separate folder for inspection by user
	if len(duplicate_medias) > 0:
		destination_drive.copy_duplicate_media_files(duplicate_medias)

	# Copy unique medias and save them in destination folder
	if len(unique_medias) > 0:
		destination_drive.copy_unique_media_files(unique_medias)

	# Wait for user input to confirm if duplicates are checked
	print()
	delete_duplicate_folder = user.confirm_yes_no(f"Check {Colors.INFO}{destination_drive.get_duplicate_folder()}{Colors.RESET} and confirm here if finished. Delete duplicate folder?")

	# If wanted - Delete duplicate copy folder
	if delete_duplicate_folder:
		destination_drive.delete_duplicate_folder()
		print(f"{Log.success('Deleted duplicate folder successfully.')}")
		print()
	else:
		print(f"{Log.success('Did not delete duplicate folder as wanted.')}")
		print()

	# Ask user if syncing with backup drive wanted (copying all existing to backup drive)
	sync_with_backup_drive = user.confirm_yes_no(f"Sync folder with backup drive (chosen in next step)?")
	if sync_with_backup_drive:
		backup_drive = user.get_backup_drive(retry=0, max_retry=5)

		if not backup_drive:
			raise Exception(Log.error('All given paths to backup drives not found.'))

		# Example 2: Dry run first (see what would happen)
		syncer = DirectorySynchronizer(source = dest_drive, destination = backup_drive)
		syncer.sync(dry_run = True)

		# If .zip file creation wanted
		create_zip_file = user.confirm_yes_no(f'\nYou also want to create {Log.info(user.get_zip_filename())}.zip file? {Log.warning('This could take multiple minutes!')}')
		if create_zip_file:
			zip_drive = user.get_zip_drive()
			if zip_drive:

				# Create .zip file at chosen drive
				zip_created = h.create_zip(folder_to_zip=destination_drive.path, save_target=zip_drive, filename=user.get_zip_filename())
				if zip_created:
					print(Log.success(f'Successfully created {Log.info(zip_drive)}\\{Log.info(user.get_zip_filename())}'))

	print()
	print(Log.finish())

def run_GUI():

	# Create instance
	window = Window()


if __name__ == "__main__":

	try:

		# Load and run program mode defined in setup
		program_mode = setup.get_program_mode()
		run_console() if program_mode == 'console' else run_GUI()

	except KeyboardInterrupt:
		print()
		print(f"Process interrupted by user.")

	except Exception as e:
		print()
		print(f"{e}")
		import traceback
		traceback.print_exc()
		print(Log.error('\nAborting execution...'))

	finally:
		input("\nPress ENTER to exit...")

