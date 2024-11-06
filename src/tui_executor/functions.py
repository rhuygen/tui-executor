"""
This module provides functionality to find specific functions, i.e. functions that are decorated
with the `@exec_task` or `@exec_recurring_task` decorators. The former, also called 'ui_button_functions'
are tasks that are associated with a button in the UI, while the latter are functions that are periodically
executed in the background.
"""
__all__ = [
    "find_ui_functions",
    "get_ui_button_functions",
    "get_ui_recurring_functions",
]

import importlib
import inspect
from typing import Callable
from typing import Dict

from .tasks import TaskKind


def get_ui_button_functions(module_path: str) -> Dict[str, Callable]:
    """
    Returns a dictionary with function names as keys and the callable function as their value.
    The functions are intended to be used as UI button callable, i.e. a UI can automatically
    identify these functions and assign them to a `clicked` action of a button.

    Args:
        module_path: string containing a fully qualified module name
    """
    return find_ui_functions(
        module_path,
        lambda x: x.__ui_kind__ & TaskKind.BUTTON
    )


def get_ui_recurring_functions(module_path: str) -> Dict[str, Callable]:
    """
    Returns a dictionary with function names as keys and the callable function as their value.
    The functions are intended to be used as recurring callables, i.e. the GUI will call these
    functions from a QTimer when the timer times out.

    Args:
        module_path: string containing a fully qualified module name
    """
    return find_ui_functions(
        module_path,
        lambda x: x.__ui_kind__ & TaskKind.RECURRING
    )


def find_ui_functions(module_path: str, predicate: Callable = None) -> Dict[str, Callable]:
    """
    Returns a dictionary with function names as keys and the callable function as their value.
    The predicate is a function that returns True or False depending on some required conditions
    for the functions that are returned.

    Args:
        module_path: string containing a fully qualified module name
        predicate: condition to select and return the function
    """
    predicate = predicate if predicate is not None else lambda x: True
    mod = importlib.import_module(module_path)

    return {
        name: member
        for name, member in inspect.getmembers(mod)
        if inspect.isfunction(member) and hasattr(member, "__ui_kind__") and predicate(member)
    }
