from __future__ import annotations

import importlib
import logging

from rich.console import RenderableType
from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import ScrollableContainer
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button
from textual.widgets import Collapsible
from textual.widgets import Label
from textual.widgets import Placeholder
from textual.widgets import RichLog
from textual.widgets import Static
from textual.widgets import TabPane

from tui_executor.arguments import ArgumentsInput
from tui_executor.funcpars import Parameter
from tui_executor.funcpars import ParameterKind
from tui_executor.funcpars import get_parameters
from tui_executor.functions import get_ui_button_functions
from tui_executor.modules import get_ui_modules
from tui_executor.tasks import TaskButton
from tui_executor.utils import format_datetime


class ArgumentsPanel(Widget):
    """
    A panel that lays out input fields for function parameters. The type of input field
    is determined by the type hint for the parameter. If no type hint is given, `str` is used
    as a default.

    The input fields for the function parameters are pre-filled with the default value if that
    default is available.

    The panel contains two buttons at the lower right:

    - a button to execute the task with the arguments filled into the input fields -> Run.
    - a button to close the panel -> Close.

    The class is called ArgumentsPanel instead of ParametersPanel because the values that you fill
    are the arguments to a function.
    """

    ALLOW_MAXIMIZE = True

    button: reactive[TaskButton | None] = reactive(None, init=True, recompose=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.button: TaskButton | None = None
        self.parameters: dict[str, Parameter] = {}
        self.input_fields: list[ArgumentsInput] = []

    def compose(self) -> ComposeResult:

        if self.button:
            with ScrollableContainer():
                if not self.input_fields:
                    yield Label(
                        f"This function \\[{self.button.function_name}()] doesn't have any arguments.",
                        id="lbl-no-arguments"
                    )

                for input_field in self.input_fields:
                    yield input_field

            with Horizontal(id="buttons-arguments-panel"):
                with Container():
                    yield Button("Maximize", id="btn-min-max-args-panel")
                    yield Button("Close", id="btn-close-args-panel")
                    yield Button("Run", id="btn-run-args-panel")
        else:
            yield Placeholder()

    def watch_button(self, button: TaskButton):
        if button:
            self.parameters = get_parameters(button.function)
            self.input_fields = [
                ArgumentsInput(parameter)
                for name, parameter in self.parameters.items()
            ]

    @property
    def function(self):
        return self.button.function if self.button else None

    @property
    def args(self):
        return [
            input_field.get_value()
            for input_field in self.input_fields
            if input_field.parameter.kind == ParameterKind.POSITIONAL_ONLY
        ]

    @property
    def kwargs(self):
        return {
            input_field.parameter.name: input_field.get_value()
            for input_field in self.input_fields
            if input_field.parameter.kind in [ParameterKind.POSITIONAL_OR_KEYWORD, ParameterKind.KEYWORD_ONLY]
        }


class ModulePanel(Static):
    """
    A collapsible panel that contains a button for each task that is defined in that module.

    The task buttons are generated from the decorated functions in a Python module. One Python
    module (`*.py` file) will correspond to one ModulePanel. The functions are decorated with
    @exec_task (or the deprecated @exec_ui).

    The title of the collapsible widget is the module name unless the variable UI_MODULE_DISPLAY_NAME
    was defined in the module.
    """
    def __init__(self, name: str, module_path: str):
        super().__init__(name=name)

        self.module_path = module_path
        self.functions = get_ui_button_functions(module_path=module_path)

        self.log.info(f"ModulePanel: {self.module_path = }, {self.functions = }")

    def compose(self) -> ComposeResult:

        # Our functions are all decorated functions, decorated with the @exec_ui or @exec_task.
        # Since we have used functools.wraps(), all our functions have the attribute __wrapped__
        # which points to the original function. What we need is the first line of the function
        # in the module file, because we want the functions to be sorted in the order they appear
        # in the source code file and not alphabetically.

        with Collapsible(title=self.name) as section:
            mod = importlib.import_module(self.module_path)
            section.tooltip = mod.__doc__
            for func_name, func in sorted(self.functions.items(), key=lambda x: x[1].__ui_lineno__):
                yield TaskButton(func_name, func)

    def is_empty(self):
        return len(self.functions) == 0


class PackagePanel(TabPane):
    """
    A TAB pane that contains all task buttons for each module in the package. The buttons are organised
    in a collapsible ModulePanel. Since there can be quite a lot of task buttons when the module panels
    are expanded.

    All (sub-)packages are TABs in the TUI. Sub-packages only go one level deep, and we start from the
    module path. So, if our package hierarchy is `tasks.shared.unit_tests` where this package contains
    Python module files (`*.py`), then module_path will be `tasks.shared` and this will generate the TAB
    `unit_tests` (unless there is a `UI_TAB_DISPLAY_NAME` defined in the `__init__.py` of that package).

    If the module_path doesn't have any sub-packages,
    Args:
        title: The title of the TabPane (will be displayed in a TabLabel)
        module_path: the full dotted module path for this package
    """
    def __init__(self, title: str, module_path: str):
        super().__init__(title=title)

        self.module_path = module_path
        self.modules = get_ui_modules(module_path=module_path)
        self.panels = {}

        self.log.info(f"PackagePanel: {self.module_path = }, {self.modules = }")

    def compose(self) -> ComposeResult:

        with VerticalScroll():

            self.panels = self._create_module_panels()
            for panel_name in sorted(self.panels):
                yield self.panels[panel_name]

    def is_empty(self):
        return len(self.modules) == 0

    def _create_module_panels(self):
        """
        Creates all collapsible panels for the modules in this package. The reason to do this before adding them to
        the TabPane is that the panels now can be sorted before adding.

        Returns:
            A dictionary containing all Collapsible ModulePanel with the display name as their key.
        """

        panels = {}

        for module_name, module in self.modules.items():
            display_name, dotted_path = module
            self.log.info(f"PackagePanel: {module_name = }, {display_name = }, {dotted_path = }")
            panel = ModulePanel(name=display_name, module_path=dotted_path)
            if not panel.is_empty():
                panels[display_name] = panel

        return panels


class ConsoleOutput(RichLog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.level_width = 8
        """The column width of the logging level, used to properly align log messages."""

        self.debug = f"[grey70]{'DEBUG':{self.level_width}}[/]"
        self.info = f"[green]{'INFO':{self.level_width}}[/]"
        self.warning = f"[dark_orange]{'WARNING':{self.level_width}}[/]"
        self.error = f"[red1]{'ERROR':{self.level_width}}[/]"

    def write_log(self, level: int, msg: RenderableType | str):

        if level == logging.DEBUG:
            self.write_log_debug(msg)
        elif level == logging.INFO:
            self.write_log_info(msg)
        elif level == logging.WARNING:
            self.write_log_warning(msg)
        elif level == logging.ERROR:
            self.write_log_error(msg)
        elif level == logging.NOTSET:
            self.write(msg)
        else:
            self.write_log_warning(
                f"The given level ({level=}) is not implemented, using default level INFO ({logging.INFO})."
            )
            self.write_log_info(msg)

    def write_log_debug(self, msg: RenderableType | str):
        self.write(f"{format_datetime(fmt='%Y-%m-%d %H:%M:%S')}: {self.debug} {msg}")

    def write_log_info(self, msg: RenderableType | str):
        self.write(f"{format_datetime(fmt='%Y-%m-%d %H:%M:%S')}: {self.info} {msg}")

    def write_log_warning(self, msg: RenderableType | str):
        self.write(f"{format_datetime(fmt='%Y-%m-%d %H:%M:%S')}: {self.warning} {msg}")

    def write_log_error(self, msg: RenderableType | str):
        self.write(f"{format_datetime(fmt='%Y-%m-%d %H:%M:%S')}: {self.error} {msg}")
