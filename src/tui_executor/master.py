import random
import textwrap

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

from .tasks import TaskButton


class MasterScreen(Screen):
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Horizontal():
            with TabbedContent():
                for package in ("Tests", "GSE", "Camera"):
                    with TabPane(title=package):
                        with VerticalScroll():
                            for module in ("Simple", "Hartmann", "Circle"):
                                with Collapsible(title=module):
                                    for task in range(random.randint(1, 5)):
                                        yield TaskButton(f"Task {task}")
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
