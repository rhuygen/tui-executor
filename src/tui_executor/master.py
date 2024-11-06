import random
import textwrap
from typing import List

from textual.app import ComposeResult
from textual.containers import Grid
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Collapsible
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import RichLog
from textual.widgets import TabPane
from textual.widgets import TabbedContent

from .modules import get_ui_subpackages
from .panels import ModulePanel
from .panels import PackagePanel
from .tasks import TaskButton


class MasterScreen(Screen):
    def __init__(self, module_path_list: List[str]):
        super().__init__()

        self.module_path_list = module_path_list

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        self.log.info(f"MasterScreen: {self.module_path_list = }")

        yield Header()
        yield Footer()

        with Horizontal():
            with TabbedContent():
                for module_path in self.module_path_list:
                    subpackages = get_ui_subpackages(module_path=module_path)

                    self.log.info(f"MasterScreen: {module_path = }, {subpackages = }")

                    if not subpackages:
                        yield PackagePanel(title=module_path, module_path=module_path)
                        continue

                    for package_name, subpackage in subpackages.items():
                        tab_name, location = subpackage
                        self.log.info(f"MasterScreen: {package_name = }, {tab_name = }, {location = }")

                        yield PackagePanel(title=tab_name, module_path=f"{module_path}.{package_name}")

            with Vertical():
                yield Grid(name="Arguments", id="arguments-panel")
                yield RichLog(max_lines=200, markup=True, id="console-log")

    def on_mount(self) -> None:
        self.query_one("#console-log", RichLog).write(textwrap.dedent(
            """\
            2024-10-16T12:14:56 [blue]tui_executor[/] INFO The TUI Executor App is ready to launch
            2024-10-16T12:14:56 [blue]tui_executor[/] INFO Composition established
            2024-10-16T12:14:57 [blue]tui_executor[/] INFO Mounting ...
            """
        ))
        self.query_one("#arguments-panel", Grid).border_title = "Arguments"
