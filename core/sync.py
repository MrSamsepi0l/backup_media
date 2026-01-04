import os
import shutil
from pathlib import Path
from dataclasses import dataclass
from core import Helper as h, Log
from alive_progress import alive_it


@dataclass
class SyncStats:
	"""Statistics for sync operation"""
	files_copied: int = 0
	files_updated: int = 0
	files_skipped: int = 0
	dirs_created: int = 0
	errors: list = None

	def __post_init__(self):
		if self.errors is None:
			self.errors = []


class DirectorySynchronizer:
	"""
	Synchronize directories incrementally - never deletes, only adds/updates
	"""

	def __init__(self, source: str, destination: str, verify_copy: bool = True):
		"""
		Args:
			source: Source directory path
			destination: Destination directory path
			verify_copy: Verify file size after copy (slower but safer)
		"""
		self.source = Path(source).resolve()
		self.destination = Path(destination).resolve()
		self.verify_copy = verify_copy
		self.stats = SyncStats()

		# Validate paths
		if not self.source.exists():
			raise ValueError(f"Source directory does not exist: {source}")
		if not self.source.is_dir():
			raise ValueError(f"Source is not a directory: {source}")

	def sync(self, dry_run: bool = False) -> SyncStats:
		"""
		Synchronize source to destination

		Args:
			dry_run: If True, only report what would be done without copying

		Returns:
			SyncStats object with operation statistics
		"""
		print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")

		# Create destination root if it doesn't exist
		if not self.destination.exists():
			if not dry_run:
				self.destination.mkdir(parents=True, exist_ok=True)
			self.stats.dirs_created += 1

		# Walk through source directory
		bar = alive_it(os.walk(self.source), title=Log.process(f"Syncing: {self.source} -> {self.destination}"), bar="brackets")
		for root, dirs, files in bar:
			root_path = Path(root)

			# Calculate relative path from source
			relative_path = root_path.relative_to(self.source)
			dest_dir = self.destination / relative_path

			# Create destination directory structure
			if not dest_dir.exists():
				if not dry_run:
					dest_dir.mkdir(parents=True, exist_ok=True)
					print(f"Created directory: {Log.success(relative_path)}")
				#else:
					#print(f"Would create directory: {Log.success(relative_path)}")
				self.stats.dirs_created += 1

			# Process files in current directory
			for filename in files:
				source_file = root_path / filename
				dest_file = dest_dir / filename

				try:
					self._sync_file(source_file, dest_file, relative_path / filename, dry_run)
				except Exception as e:
					error_msg = f"Error syncing {Log.error(source_file)}: {str(e)}"
					self.stats.errors.append(error_msg)
					print(f"{error_msg}")

		# Print summary
		self._print_summary()
		return self.stats

	def _sync_file(self, source_file: Path, dest_file: Path, relative_path: Path, dry_run: bool):
		"""Sync a single file"""

		# File doesn't exist in destination - copy it
		if not dest_file.exists():
			if not dry_run:
				shutil.copy2(source_file, dest_file)  # copy2 preserves metadata

				if self.verify_copy and dest_file.stat().st_size != source_file.stat().st_size:
					raise ValueError(f"Size mismatch after copy")

				self.stats.files_copied += 1
				print(f"Copied: {Log.success(relative_path)}")
			else:
				self.stats.files_copied += 1
				#print(f"Would copy: {Log.success(relative_path)}")
			return

		# File exists - check if update needed
		source_mtime = source_file.stat().st_mtime
		dest_mtime = dest_file.stat().st_mtime
		source_size = source_file.stat().st_size
		dest_size = dest_file.stat().st_size

		# Update if source is newer or size differs
		if source_mtime > dest_mtime or source_size != dest_size:
			if not dry_run:
				shutil.copy2(source_file, dest_file)

				if self.verify_copy and dest_file.stat().st_size != source_file.stat().st_size:
					raise ValueError(f"Size mismatch after update")

				self.stats.files_updated += 1
				print(f"Updated: {Log.warning(relative_path)}")
			else:
				self.stats.files_updated += 1
				print(f"Would update: {Log.warning(relative_path)}")
		else:
			# File is up-to-date
			self.stats.files_skipped += 1
			# Uncomment to see skipped files:
			# print(f"Skipped (up-to-date): {relative_path}")

	def _print_summary(self):
		"""Print operation summary"""
		print(f"Directories created: {Log.success(self.stats.dirs_created)}")
		print(f"Files copied:        {Log.success(self.stats.files_copied)}")
		print(f"Files updated:       {Log.warning(self.stats.files_updated)}")
		print(f"Files skipped:       {Log.info(self.stats.files_skipped)}")
		print(f"Errors:              {Log.error(len(self.stats.errors))}")

		if self.stats.errors:
			print("\nErrors encountered:")
			for error in self.stats.errors:
				print(f"  - {error}")

		total_operations = (self.stats.dirs_created + self.stats.files_copied +
						  self.stats.files_updated)
		print(f"Total operations:    {total_operations}")