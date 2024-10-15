from textual.app import App
from textual.binding import Binding

from .help import HelpScreen
from .master import MasterScreen


class TuiExecutorApp(App):

    CSS_PATH = "app.tcss"
    SCREENS = {"master": MasterScreen, "help": HelpScreen}
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding(key="f1", action="help", description="Help", show=True, priority=True),
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]

    def on_mount(self):
        self.push_screen("master")

    def action_help(self) -> None:
        if self.screen != self.get_screen("help"):
            self.app.push_screen(self.get_screen("help"))
