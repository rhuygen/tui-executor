__all__ = [
    "TaskButton",
    "TaskKind",
]

import sys
import textwrap
from enum import IntEnum
from typing import Callable

from textual.widgets import Button

from tui_executor import MAX_WIDTH_FUNCTION_NAME


def get_task_button_label(func: Callable, label: str = None, triangles: bool = False) -> str:
    """
    Determine the label for the task button associated to the given function. If the task was
    given a display name, that will have precedence over the given label. If both are None,
    the function name will be returned.

    The label can have a maximum length of MAX_WIDTH_FUNCTION_NAME, which is defined in `tui-executor.__init__`.

    Args:
        func: the function that is associated with the button
        label: an optional label that will have precedence over the function name as a label
        triangles: Put ▶ function ◀ around the button label

    Returns:
        A string representing the label for the button.
    """
    if hasattr(func, "__ui_display_name__") and func.__ui_display_name__:
        name = func.__ui_display_name__
    else:
        name = label or func.__name__

    # The following line will put the display_name within triangles: ▶︎ name ◀︎
    # when the immediate_run flag is True.

    if triangles and hasattr(func, "__ui_immediate_run__") and func.__ui_immediate_run__:
        width = MAX_WIDTH_FUNCTION_NAME - 4  # another_function_with_an_extra..
        prefix = "\u25B6 "
        postfix = " \u25C0"
    else:
        width = MAX_WIDTH_FUNCTION_NAME
        prefix = postfix = ""

    if len(name) > width:
        dots = ".."
        width -= 2
    else:
        dots = ""

    name = f"{prefix}{name[:width]}{dots}{postfix}"

    return name


class TaskKind(IntEnum):
    BUTTON = 0b00000001
    """Identifies a function to be called after a clicked event on a button in the GUI."""
    RECURRING = 0b00000010
    """Identifies a function to be called recurrently with a timer from the GUI."""


class TaskButton(Button):
    """
    A button that represents a task. Pressing the button will open its arguments panel.
    """

    def __init__(self, name: str, function: Callable):
        super().__init__(name=name)

        self.label = get_task_button_label(function, triangles=True)  # noqa
        self._function = function

        if function.__doc__:
            self.tooltip = f"[b]{function.__name__}[/]\n" + textwrap.dedent(function.__doc__)

    def on_mount(self):
        if self.immediate_run:
            self.add_class("immediate_run")

    @property
    def immediate_run(self) -> bool:
        if hasattr(self._function, "__ui_immediate_run__"):
            return self._function.__ui_immediate_run__
        return False

    @property
    def function(self) -> Callable:
        return self._function

    @property
    def function_name(self) -> str:
        return self._function.__name__

    @property
    def function_display_name(self) -> str:
        if hasattr(self._function, "__ui_display_name__") and self._function.__ui_display_name__:
            return self._function.__ui_display_name__
        return ""

    @property
    def module_name(self) -> str:
        """Returns the name of the module where the function resides."""
        if hasattr(self._function, "__ui_module__"):
            return self._function.__ui_module__
        else:
            return ""

    @property
    def module_display_name(self) -> str:
        try:
            try:
                # This attribute is given to the function when copying the function object
                # to be used in a different TAB with another display name
                return self._function.__ui_module_display_name__
            except AttributeError:
                return sys.modules[self._function.__ui_module__].UI_MODULE_DISPLAY_NAME
        except (AttributeError, KeyError):
            return self.module_name.rsplit(".", 1)[-1]
