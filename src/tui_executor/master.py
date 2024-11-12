from __future__ import annotations

import importlib
import logging
from typing import List

from textual import on
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import TabbedContent

from .dialogs import YesNoDialog
from .funcpars import get_parameters
from .functions import run_function
from .kernel import MyKernel
from .kernel import start_kernel
from .modules import get_ui_subpackages
from .panels import ConsoleOutput
from .panels import PackagePanel
from .tasks import TaskButton
from .utils import extract_var_name_args_and_kwargs


class ConsoleMessage(Message):
    def __init__(self, message: str, level: int = logging.INFO):
        super().__init__()
        self.message = message
        self.level = level


class MasterScreen(Screen):

    BINDINGS = [
        Binding("k", "start_kernel", "Start a kernel"),
    ]

    def __init__(self, module_path_list: List[str]):
        super().__init__()

        self.module_path_list = module_path_list
        self.tabs = {}

        self.kernel: MyKernel | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Header()
        yield Footer()

        with Horizontal():
            with TabbedContent():

                self.tabs = self._create_tabs()
                for tab_name in sorted(self.tabs):
                    yield self.tabs[tab_name]

            with Vertical():
                yield Grid(name="Arguments", id="arguments-panel")
                yield ConsoleOutput(max_lines=200, markup=True, id="console-log")

    def on_mount(self) -> None:
        self.query_one("#console-log", ConsoleOutput).write_log_info("The TUI Executor App is ready to launch.")
        self.query_one("#console-log", ConsoleOutput).write_log_info("Composition established.")
        self.query_one("#console-log", ConsoleOutput).write_log_info("Mounting ...")

        self.query_one("#arguments-panel", Grid).border_title = "Arguments"

    @work()
    async def action_start_kernel(self, force: bool = False) -> None:

        name = "python3"  # get the kernel name from a widget or from a the command panel

        # Starting the kernel will need a proper PYTHONPATH for importing the packages

        if force:
            if self.kernel is not None:
                self.query_one("#console-log", ConsoleOutput).write_log_info("Shutdown kernel...")
                self.kernel.shutdown()
            self.query_one("#console-log", ConsoleOutput).write_log_info("Starting kernel (forced)...")
            self.kernel = start_kernel(name)
            return

        if self.kernel is None:
            self.query_one("#console-log", ConsoleOutput).write_log_info("Starting kernel...")
            self.kernel = start_kernel(name)
        else:
            if await self.app.push_screen_wait(
                YesNoDialog(title="Restart Jupyter kernel",
                            question="A kernel is running, should a new kernel be started?")
            ):
                self.query_one("#console-log", ConsoleOutput).write_log_info("Shutdown kernel...")
                self.kernel.shutdown()
                self.query_one("#console-log", ConsoleOutput).write_log_info("Starting new kernel...")
                self.kernel = start_kernel(name)

    @on(TaskButton.Pressed)
    def run_task(self, event: TaskButton.Pressed):
        button: TaskButton = event.button

        self.log.info(f"TaskButton: {event = }, {type(event) = }, {button = }")

        if button.immediate_run():
            self.query_one(ConsoleOutput).write_log_info(
                f"Task {button.function.__name__} is run immediately when pressed."
            )

            ui_pars = get_parameters(button.function)
            args, kwargs = extract_var_name_args_and_kwargs(ui_pars)
            run_function(button.function, args, kwargs, notify=self.send_to_console)

            return

        self.query_one(ConsoleOutput).write_log_info("Preparing the ArgumentsPanel..")

        # Prepare and show the ArgumentsPanel. The function will be executed when the Run button is pressed in the
        # ArgumentsPanel.

        ...

    def send_to_console(self, message: str, level: int = logging.INFO):
        self.post_message(ConsoleMessage(message, level=level))

    def on_console_message(self, message: ConsoleMessage):
        self.query_one(ConsoleOutput).write_log(message.level, message.message)

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
