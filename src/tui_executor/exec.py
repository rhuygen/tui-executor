from __future__ import annotations
"""
This module provides the decorators for defining Tasks.
"""
__all__ = [
    "StatusType",
    "exec_recurring_task",
    "exec_task",
    "exec_ui",
]

from enum import IntEnum
from functools import wraps
from pathlib import Path
from typing import Tuple

from . import RUNNABLE_APP
from . import RUNNABLE_KERNEL
from . import RUNNABLE_SCRIPT
from .tasks import TaskKind


class StatusType(IntEnum):
    PERMANENT = 1
    """Use the permanent widget to show the message in the status bar."""
    NORMAL = 2
    """Use the """


def exec_recurring_task(
        kind: TaskKind = TaskKind.RECURRING,
        status_type: StatusType = None,
):
    """
    Decorator for a recurring task. The function will be executed as a background task (a thread or a co-routine)
    at periodic intervals.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # you can put extra code to be run here, based on the arguments to exec_ui
            response = func(*args, **kwargs)
            # or here
            return response

        wrapper.__ui_kind__ = kind
        wrapper.__ui_status_type__ = status_type

        return wrapper

    return decorator


def exec_task(
        kind: TaskKind = TaskKind.BUTTON,
        description: str = None,
        display_name: str = None,
        input_request: Tuple[str, ...] = None,
        use_kernel: bool = False,
        use_gui_app: bool = False,
        use_script_app: bool = False,
        icons: Tuple[str | Path, ...] = None,
        immediate_run: bool = False,
        allow_kernel_interrupt: bool = False,
        capture_response: str | tuple[str, ...] = "response",
):
    """
    Decorates the function as an executable task in the TUI Executor. The function will appear in the TUI
    as a button to execute the function.

    Args:
        kind: identifies the function and what it can be used for [default = BUTTON]
        description: short function description intended to be used as tooltip or similar
        display_name: the string to use for the button name [default = function name]
        input_request: a tuple contain the string to detect when input is asked for
        use_kernel: use the Jupyter kernel when running this function
        use_gui_app: run the script in a GUI app (enables showing plots and table etc.
        use_script_app: run the script as a plain Python script [this is the default if none is specified]
        icons: icons to be used for the button of this function
        immediate_run: when True execute the function immediately when pressed without creating and
            presenting the arguments panel with the Run button
        allow_kernel_interrupt: allow this GUI to interrupt the kernel before running this task
        capture_response: replace the response to capture return values in different variables

    Returns:
        The wrapper function object.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # you can put extra code to be run here, based on the arguments to exec_ui
            response = func(*args, **kwargs)
            # or here
            return response
        wrapper.__ui_kind__ = kind
        wrapper.__ui_description__ = description
        wrapper.__ui_display_name__ = display_name
        wrapper.__ui_file__ = func.__code__.co_filename
        wrapper.__ui_lineno__ = func.__code__.co_firstlineno
        wrapper.__ui_module__ = func.__module__
        wrapper.__ui_input_request__ = input_request
        wrapper.__ui_immediate_run__ = immediate_run
        wrapper.__ui_icons__ = icons
        wrapper.__ui_allow_kernel_interrupt__ = allow_kernel_interrupt
        wrapper.__ui_capture_response__ = capture_response if isinstance(capture_response, str) else ", ".join(capture_response)
        if use_script_app:
            wrapper.__ui_runnable__ = RUNNABLE_SCRIPT
        elif use_kernel:
            wrapper.__ui_runnable__ = RUNNABLE_KERNEL
        elif use_gui_app:
            wrapper.__ui_runnable__ = RUNNABLE_APP
        else:
            wrapper.__ui_runnable__ = RUNNABLE_KERNEL

        return wrapper

    return decorator


exec_ui = exec_task
