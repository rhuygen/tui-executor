__all__ = [
    "TaskButton",
    "ButtonPanel",
    "TaskKind",
]

from enum import IntEnum

from textual.widgets import Button
from textual.widgets import Collapsible


class TaskKind(IntEnum):
    BUTTON = 0b00000001
    """Identifies a function to be called after a clicked event on a button in the GUI."""
    RECURRING = 0b00000010
    """Identifies a function to be called recurrently with a timer from the GUI."""


class TaskButton(Button):
    def __init__(self, name: str):
        super().__init__(name=name)
        self._name = name


class ButtonPanel(Collapsible):
    """
    A ButtonPanel is a collapsible widget that contains task buttons. The task buttons are generated from
    the decorated functions in a Python module. One Python module (`*.py` file) will correspond to one ButtonPanel.
    The functions are decorated with @exec_task (or the deprecated @exec_ui).

    The title of the collapsible widget is the module name unless the variable UI_MODULE_DISPLAY_NAME was defined
    in the module.
    """
    def __init__(self, title: str):
        super().__init__(title=title)

        self.task_buttons = []

    def add_button(self, button: TaskButton):
        self.task_buttons.append(button)
