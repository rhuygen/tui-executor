import importlib
import textwrap
from typing import List

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.events import Event
from textual.screen import Screen
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import RichLog
from textual.widgets import TabbedContent

from .funcpars import get_parameters
from .functions import run_function
from .modules import get_ui_subpackages
from .panels import PackagePanel
from .tasks import TaskButton
from .utils import extract_var_name_args_and_kwargs


class MasterScreen(Screen):
    def __init__(self, module_path_list: List[str]):
        super().__init__()

        self.module_path_list = module_path_list
        self.tabs = {}

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        self.log.info(f"MasterScreen: {self.module_path_list = }")

        yield Header()
        yield Footer()

        with Horizontal():
            with TabbedContent():

                self.tabs = self._create_tabs()
                for tab_name in sorted(self.tabs):
                    yield self.tabs[tab_name]

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

    @on(TaskButton.Pressed)
    def run_task(self, event: Event):
        button: TaskButton = event.button

        self.log.info(f"TaskButton: {event = }, {type(event) = }, {button = }")

        if button.immediate_run():
            self.log.info("Task is run immediately when pressed.")

            ui_pars = get_parameters(button.function)
            args, kwargs = extract_var_name_args_and_kwargs(ui_pars)
            run_function(button.function, args, kwargs, button.function.__ui_runnable__)

        self.log.info("Preparing the ArgumentsPanel..")

        # Prepare and show the ArgumentsPanel. The function will be executed when the Run button is pressed in the
        # ArgumentsPanel.

        ...

    def _create_tabs(self):
        """
        Creates all TABs for the sub-packages in the module_path_list. The reason to do this before adding them to
        the TabContent is that the TABs now can be sorted before adding.

        Returns:
            A dictionary containing all PackagePanel TabPanes with the display name as their key.
        """
        tabs = {}

        for module_path in self.module_path_list:
            subpackages = get_ui_subpackages(module_path=module_path)

            self.log.info(f"MasterScreen: {module_path = }, {subpackages = }")

            if not subpackages:
                tab_name = get_tab_name(module_path)
                tab = PackagePanel(title=tab_name, module_path=module_path)
                if not tab.is_empty():
                    tabs[tab_name] = tab
                continue

            for package_name, subpackage in subpackages.items():
                tab_name, location = subpackage
                self.log.info(f"MasterScreen: {package_name = }, {tab_name = }, {location = }")

                tab = PackagePanel(title=tab_name, module_path=f"{module_path}.{package_name}")
                if not tab.is_empty():
                    tabs[tab_name] = tab

        return tabs


def get_tab_name(module_path: str, name: str = None):
    mod = importlib.import_module(module_path)
    name = name or module_path.split('.')[-1]

    display_name = getattr(mod, "UI_TAB_DISPLAY_NAME", name)

    return display_name
