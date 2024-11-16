from typing import List

from textual.app import App
from textual.binding import Binding
from textual.reactive import var

from .help import HelpScreen
from .master import MasterScreen


class TuiExecutorApp(App):

    CSS_PATH = "app.tcss"
    SCREENS = {"master": MasterScreen, "help": HelpScreen}
    TOOLTIP_DELAY = 1.2  # seconds before tooltip is shown
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding(key="f1", action="help", description="Help", show=True, priority=True),
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]

    settings: dict = var(dict)

    def __init__(self, module_path_list: List[str]):
        super().__init__()

        self.module_path_list = module_path_list
        self.settings['show-code-snippet'] = True

    def on_mount(self):
        self.push_screen(MasterScreen(self.module_path_list))

    def action_help(self) -> None:
        if self.screen != self.get_screen("help"):
            self.app.push_screen(self.get_screen("help"))
