from typing import Dict

from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Vertical
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible
from textual.widgets import Label
from textual.widgets import Static
from textual.widgets import TabPane

from tui_executor.funcpars import Parameter
from tui_executor.funcpars import get_parameters
from tui_executor.functions import get_ui_button_functions
from tui_executor.modules import get_ui_modules
from tui_executor.modules import get_ui_subpackages
from tui_executor.tasks import TaskButton


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

    def __init__(self, button: TaskButton):
        super().__init__()

        self._button = button
        self._pars: Dict[str, Parameter] = get_parameters(button.function)

    def compose(self) -> ComposeResult:

        with VerticalScroll():
            for name, parameter in self._pars.items():
                yield Label(name)


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

        with Collapsible(title=self.name):
            for func_name, func in self.functions.items():
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
