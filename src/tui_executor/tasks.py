__all__ = [
    "TaskButton",
    "TaskKind",
]

from enum import IntEnum
from typing import Callable

from textual.widgets import Button


def get_task_button_label(func: Callable, label: str = None) -> str:
    """
    Determine the label for the task button associated to the given function. If the task was
    given a display name, that will have precedence over the given label. If both are None,
    the function name will be returned.

    Args:
        func: the function that is associated with the button
        label: an optional label that will have precedence over the function name as a label

    Returns:
        A string representing the label for the button.
    """
    if hasattr(func, "__ui_display_name__") and func.__ui_display_name__:
        return func.__ui_display_name__
    else:
        return label or func.__name__


class TaskKind(IntEnum):
    BUTTON = 0b00000001
    """Identifies a function to be called after a clicked event on a button in the GUI."""
    RECURRING = 0b00000010
    """Identifies a function to be called recurrently with a timer from the GUI."""


class TaskButton(Button):
    """
    A button that represents a task. Pressing the button will open its arguments panel.
    """

    DEFAULT_CSS = """
    TaskButton {
        min-width: 80%;
    }
    """

    def __init__(self, name: str, function: Callable):
        super().__init__(name=name)

        self.label = get_task_button_label(function)  # noqa
        self.function = function
