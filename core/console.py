from cmd_menu import CmdMenu

def open_cmd_select_menu(options = ["Start", "Settings"]):
	"""
	Uses CMD selection menu to show interactive menu
	for the user to select the device where to save from.
	"""

	# Open and run CmdMenu
	cmd_menu = CmdMenu(options, "Choose connected drive/device...")
	option = cmd_menu.run()

	# Return selected option
	return option