from __future__ import annotations

import asyncio
import importlib
import logging
import sys
import traceback
from queue import Queue
from typing import Callable
from typing import Dict
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
from textual.worker import Worker
from textual.worker import WorkerState

from .dialogs import YesNoDialog
from .funcpars import get_parameters
from .kernel import MyKernel
from .kernel import start_kernel
from .modules import get_ui_subpackages
from .panels import ConsoleOutput
from .panels import PackagePanel
from .runnables import FunctionRunnableKernel
from .tasks import TaskButton
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
        Binding("k", "start_kernel", "Start a kernel"),
    ]

    def __init__(self, module_path_list: List[str]):
        super().__init__()

        self.module_path_list = module_path_list
        self.tabs = {}

        self.kernel: MyKernel | None = None
        self.input_queue: Queue = Queue()

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
                yield Grid(name="Arguments", id="arguments-panel")
                yield ConsoleOutput(max_lines=200, markup=True, highlight=False, id="console-log")

    def on_mount(self) -> None:
        self.query_one("#console-log", ConsoleOutput).write_log_info("The TUI Executor App is ready to launch.")
        self.query_one("#console-log", ConsoleOutput).write_log_info("Composition established.")
        self.query_one("#console-log", ConsoleOutput).write_log_info("Mounting ...")

        self.query_one("#arguments-panel", Grid).border_title = "Arguments"
        self.query_one("#console-log", ConsoleOutput).border_title = "Console Output"

        self.set_timer(0.2, self._start_kernel)

    async def _start_kernel(self):
        self.action_start_kernel()

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

    @on(TaskButton.Pressed)
    async def run_task(self, event: TaskButton.Pressed):
        button: TaskButton = event.button

        self.log.debug(f"TaskButton: {event = }, {type(event) = }, {button = }")

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

            ui_pars = get_parameters(button.function)
            args, kwargs = extract_var_name_args_and_kwargs(ui_pars)
            self.run_function(
                button.function, args, kwargs,
                input_queue=self.input_queue, kernel=self.kernel, notify=self.send_to_console
            )

            # self.query_one("#all-tasks", TabbedContent).disabled = False

            return

        self.query_one(ConsoleOutput).write_log_info("Preparing the ArgumentsPanel..")

        # Prepare and show the ArgumentsPanel. The function will be executed when the Run button is pressed in the
        # ArgumentsPanel.

        ...

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
            # response = func(*args, **kwargs)
            # thread = FunctionRunnableCurrentInterpreter(func, args, kwargs, input_queue, notify)
            thread = FunctionRunnableKernel(kernel, func, args, kwargs, input_queue, notify)
            thread.start()

            # What if the function takes a long time to finish or ends up in an infinite loop?
            # The loop below ensures the TUI stays responsive.

            while thread.is_running():
                await asyncio.sleep(0.1)

            thread.join()
            response = thread.response()

            # with MyClient(kernel) as client:
            #     snippet = create_code_snippet(func, args, kwargs)
            #
            #     notify("The code snippet:", level=logging.NOTSET)
            #     notify(create_code_snippet_renderable(func, args, kwargs), level=logging.NOTSET)
            #     notify("", level=logging.NOTSET)
            #
            #     cmd, out, err = client.run_snippet(snippet, notify=notify)
            #
            #     # if out:
            #     #     notify(Text.from_ansi('\n'.join(out)), level=logging.NOTSET)
            #     if err:
            #         notify(Text.from_ansi('\n'.join(err)), level=logging.NOTSET)

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
                parameters = ', '.join(args)
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
