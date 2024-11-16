from __future__ import annotations

import asyncio
import importlib
import logging
import sys
import textwrap
import traceback
from queue import Queue
from typing import Callable
from typing import Dict
from typing import List

from textual import on
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import TabbedContent
from textual.worker import Worker
from textual.worker import WorkerState

from .dialogs import SelectDialog
from .dialogs import YesNoDialog
from .funcpars import get_parameters
from .kernel import MyKernel
from .kernel import find_running_kernels
from .kernel import start_kernel
from .modules import get_ui_subpackages
from .panels import ArgumentsPanel
from .panels import ConsoleOutput
from .panels import PackagePanel
from .runnables import FunctionRunnableKernel
from .tasks import TaskButton
from .utils import create_code_snippet_renderable
from .utils import extract_var_name_args_and_kwargs

DEBUG = False
"""Enable/disable all debugging log messages in this module."""


class ConsoleMessage(Message):
    def __init__(self, message: str, level: int = logging.INFO):
        super().__init__()
        self.message = message
        self.level = level


class MasterScreen(Screen):

    BINDINGS = [
        Binding("k", "start_kernel", "Start a kernel",
                tooltip="Starts a new kernel. Asks confirmation if a kernel is running."),
        Binding('K', "use_kernel", "Use an existing kernel", show=False)
    ]

    def __init__(self, module_path_list: List[str]):
        super().__init__()

        self.module_path_list = module_path_list
        self.tabs = {}

        self.own_kernels: set = set()
        """Kernels that are created and owned by this app. Will be shutdown when app terminates."""
        self.kernel: MyKernel | None = None
        self.input_queue: Queue = Queue()
        self.arguments_panel: ArgumentsPanel | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Header()
        yield Footer()

        with Horizontal():
            with TabbedContent(id="all-tasks"):

                self.tabs = self._create_tabs()
                for tab_name in sorted(self.tabs):
                    yield self.tabs[tab_name]

            with Vertical():
                yield ArgumentsPanel(name="Arguments", id="arguments-panel")
                yield ConsoleOutput(max_lines=200, markup=True, highlight=False, id="console-log")

    def on_mount(self) -> None:
        self.query_one("#arguments-panel", ArgumentsPanel).border_title = "Arguments"
        self.query_one("#arguments-panel", ArgumentsPanel).display = False
        self.query_one("#console-log", ConsoleOutput).border_title = "Console Output"

        self.set_timer(0.2, self._start_kernel)

    async def _start_kernel(self):

        kernels = list(find_running_kernels())
        if kernels:
            self.action_use_kernel(kernels)
        else:
            self.action_start_kernel()

    @work()
    async def action_use_kernel(self, kernels: list[MyKernel] = None):
        kernels = kernels or list(find_running_kernels())

        kernel_options = [
            (
                f"{kernel.get_display_name()} [PID={kernel.get_pid()}"
                f"{', current kernel' if self.kernel and kernel.get_pid() == self.kernel.get_pid() else ''}]"
            ) for kernel in kernels
        ]

        index = await self.app.push_screen_wait(
            SelectDialog(
                kernel_options,
                title="Select an existing kernel",
                message=textwrap.dedent(
                    """\
                    Below is a list of kernels currently running on your system. 
                    If you want to connect to one of these existing kernels, select the kernel from the list below.
                    Press 'OK' to confirm the selection, press 'Cancel' to discard and start a new kernel.
                    """
                )
            )
        )
        # self.query_one("#console-log", ConsoleOutput).write_log_info(f"Selected index = {index}")

        if 0 <= index < len(kernels):
            kernel = kernels[index]
            self.query_one("#console-log", ConsoleOutput).write_log_info(f"Using kernel...{kernel_options[index]}")
            if self.kernel:
                if kernel.get_pid() != self.kernel.get_pid():
                    self.kernel.shutdown()
                    self.kernel = kernel
            else:
                self.kernel = kernel
        else:
            if not self.kernel:
                self.action_start_kernel(force=False)

    @work()
    async def action_start_kernel(self, force: bool = False) -> None:

        name = "python3"  # get the kernel name from a widget or from the command panel

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

    @on(Button.Pressed)
    async def run_task(self, event: Button.Pressed):
        button: Button = event.button

        self.log.debug(f"TaskButton: {event = }, {type(event) = }, {button = }, {button.id = }")

        if not self.kernel:
            self.post_message(ConsoleMessage("No kernel is  running, task cannot be executed.", level=logging.WARNING))
            return

        # First handle the buttons from the arguments panel to run the task and manipulate the size of the panel.

        if button.id == "btn-run-args-panel":
            self.minimize()

            args_panel = self.query_one(ArgumentsPanel)

            self.run_function(
                args_panel.button.function, args_panel.args, args_panel.kwargs,
                input_queue=self.input_queue, kernel=self.kernel, notify=self.send_to_console
            )

        elif button.id == "btn-close-args-panel":
            args_panel = self.query_one(ArgumentsPanel)
            args_panel.button = None
            args_panel.display = False
            self.minimize()

        elif button.id == "btn-min-max-args-panel":
            args_panel = self.query_one(ArgumentsPanel)
            if args_panel.is_maximized:
                self.minimize()
                button.label = "Maximize"
            else:
                self.maximize(args_panel)
                button.label = "Minimize"

        # The handle the actual execution of the task.

        elif isinstance(button, TaskButton):
            if DEBUG:
                msg = (
                    f"Some debugging information on the button:\n"
                    f"Button name: {button.name}\n"
                    f"Button module_name: {button.module_name}\n"
                    f"Button module_display_name: {button.module_display_name}\n"
                    f"Button label: {button.label}\n"
                    f"Button function: {button.function}\n"
                    f"Button function_name: {button.function_name}\n"
                    f"Button function_display_name: {button.function_display_name}\n"
                    f"Immediate run: {button.immediate_run}\n"
                )
                self.query_one(ConsoleOutput).write_log_debug(msg)

            if button.immediate_run:
                DEBUG and self.query_one(ConsoleOutput).write_log_info(
                    f"Task {button.function.__name__} is run immediately when pressed."
                )
                self.query_one(ArgumentsPanel).display = False

                ui_pars = get_parameters(button.function)
                self.log.info(f"{ui_pars = }")

                args, kwargs = extract_var_name_args_and_kwargs(ui_pars)
                self.log.info(f"{args = }, {kwargs = }")

                self.run_function(
                    button.function, args, kwargs,
                    input_queue=self.input_queue, kernel=self.kernel, notify=self.send_to_console
                )

            else:
                self.query_one(ArgumentsPanel).button = button
                self.query_one(ArgumentsPanel).display = True

    def send_to_console(self, message: str, level: int = logging.INFO):
        self.post_message(ConsoleMessage(message, level=level))

    def on_console_message(self, message: ConsoleMessage):
        self.query_one(ConsoleOutput).write_log(message.level, message.message)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""

        if event.worker.name == "run_function":
            if event.state == WorkerState.RUNNING:
                self.query_one("#all-tasks", TabbedContent).disabled = True
            elif event.state in (WorkerState.SUCCESS, WorkerState.ERROR, WorkerState.CANCELLED):
                self.query_one("#all-tasks", TabbedContent).disabled = False

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

    @work()
    async def run_function(
            self,
            func: Callable, args: List, kwargs: Dict,
            input_queue: Queue = None,
            runnable_type: int = None,
            kernel: MyKernel = None,
            notify: Callable = lambda x, y: ...
    ):

        runnable_type = runnable_type or func.__ui_runnable__

        try:
            if self.app.settings.get('show-code-snippet', False):
                notify(create_code_snippet_renderable(func, args, kwargs), level=logging.NOTSET)
                notify("", level=logging.NOTSET)

            thread = FunctionRunnableKernel(kernel, func, args, kwargs, input_queue, notify)
            thread.start()

            # What if the function takes a long time to finish or ends up in an infinite loop?
            # The loop below ensures the TUI stays responsive.

            while thread.is_running():
                await asyncio.sleep(0.1)

            thread.join()
            response = thread.response()

            # notify(f"{response = }")

            if isinstance(response, Exception):
                raise response

        except Exception as exc:
            # TODO: This shall be sent to the Output console with proper formatting
            notify(f"Caught {exc.__class__.__name__}: {exc}", level=logging.INFO)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.extract_tb(exc_traceback)
            err_msg = "\n"
            for filename, lineno, fn, text in traceback_details:
                err_msg += (
                    f"{'-' * 80}\n"
                    f"In File    : {filename}\n"
                    f"At Line    : {lineno}\n"
                    f"In Function: {fn}\n"
                    f"Code       : {text}\n"
                    f"Exception  : {exc_value}\n"
                )
            notify(err_msg, level=logging.ERROR)
        else:
            parameters = ""
            if args:
                parameters = ', '.join([str(x) for x in args])
            if kwargs:
                if parameters:
                    parameters += ', '
                parameters += ', '.join([f"{k}={v}" for k, v in kwargs.items()])

            # notify(f"run_function: {func.__name__}({parameters}) -> {out = }", level=logging.INFO)


def get_tab_name(module_path: str, name: str = None):
    mod = importlib.import_module(module_path)
    name = name or module_path.split('.')[-1]

    display_name = getattr(mod, "UI_TAB_DISPLAY_NAME", name)

    return display_name
