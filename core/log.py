from data.colors import Colors

class Log:

	@staticmethod
	def success(text):
		return f"{Colors.SUCCESS}{text}{Colors.RESET}"

	@staticmethod
	def error(text):
		return f"{Colors.DANGER}{text}{Colors.RESET}"

	@staticmethod
	def warning(text):
		return f"{Colors.WARNING}{text}{Colors.RESET}"

	@staticmethod
	def info(text):
		return f"{Colors.INFO}{text}{Colors.RESET}"

	@staticmethod
	def muted(text):
		return f"{Colors.TEXT_MUTED}{text}{Colors.RESET}"

	@staticmethod
	def bold(text):
		return f"{Colors.TEXT_BOLD}{text}{Colors.RESET}"

	@staticmethod
	def process(text):
		return f"{Colors.PROCESS}{text}{Colors.RESET}"

	@staticmethod
	def finish():

		return ("""
███████╗██╗███╗   ██╗██╗███████╗██╗  ██╗███████╗██████╗
██╔════╝██║████╗  ██║██║██╔════╝██║  ██║██╔════╝██╔══██╗
█████╗  ██║██╔██╗ ██║██║███████╗███████║█████╗  ██║  ██║
██╔══╝  ██║██║╚██╗██║██║╚════██║██╔══██║██╔══╝  ██║  ██║
██║     ██║██║ ╚████║██║███████║██║  ██║███████╗██████╔╝
╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═════╝
		  """)