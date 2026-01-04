from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import Label, Box, Frame
from prompt_toolkit.styles import Style

class CmdMenu:

	def __init__(self, options, title="Select an option"):
		self.options = options
		self.index = 0
		self.title = title
		self.selected = None

		# UI Style
		self.style = Style.from_dict({
			"frame": "bg:#202020 #ffffff",
			"option": "bg:#303030 #aaaaaa",
			"highlighted": "bg:#00aaff #000000 bold",
			"title": "bg:#00aaff #000000 bold",
			})

		# Key bindings
		self.kb = KeyBindings()

		@self.kb.add("up")
		def move_up(event):
			self.index = (self.index - 1) % len(self.options)

		@self.kb.add("down")
		def move_down(event):
			self.index = (self.index + 1) % len(self.options)

		@self.kb.add("enter")
		def select(event):
			self.selected = self.options[self.index]
			event.app.exit()

		# Create *static* UI container
		self.option_label = [
			Label("", style="class:option") for _ in self.options
		]

		self.body = HSplit(self.option_label)
		self.root_container = Frame(
			Box(self.body, padding = 1),
			title = self.title,
			style = "class:frame"
		)

	def update_ui(self):
		"""Update text + highlighting without recreating widgets."""
		for i, text in enumerate(self.options):
			prefix = "➤  " if i == self.index else "  "
			style  = "class:highlighted" if i == self.index else "class:option"
			self.option_label[i].text = prefix + str(text)
			self.option_label[i].style = style

	def run(self):

		app = Application(
			layout = Layout(self.root_container),
			key_bindings = self.kb,
			style = self.style,
			full_screen = False,
		)

		# Update layout dynamically on each UI render
		app.pre_run_callables.append(self.update_ui)
		app.before_render += lambda _: self.update_ui()

		# Run the selection menu
		app.run()
		return self.selected