"""
This module contains functions that are executed immediately after their
associated buttons are pressed. Each task demonstrates a particular feature
of immediate run tasks. You can hover over the tasks to get more detailed
information.
"""
import platform
import textwrap
from pathlib import Path

import textual

from tui_executor import DEFAULT_CONSOLE_OUTPUT_WIDTH
from tui_executor.exec import exec_task
from tui_executor.version import get_version

HERE = Path(__file__).parent.resolve()
ICON_PATH = HERE / "../../../../src/tui_executor/icons/"


@exec_task(immediate_run=True)
def print_sys_path():
    import sys
    import rich

    rich.print(sys.path)


@exec_task(immediate_run=True)
def print_versions():
    """Print the versions of Python, Textual, and TUI Executor."""
    import rich

    rich.print(textwrap.dedent(
        f"""\
        Python version   : {platform.python_version()}
        Textual version  : {textual.__version__}
        TUI Executor Tool: {get_version()} 
        """
    ))


@exec_task(immediate_run=True)
def print_arguments(a: int = 42, b: float = 3.14, c: str = "default"):
    """
    This task prints its arguments as a string with Rich markup. That output
    shall be captured and printed in output console panel. Nothing is returned
    by this task.
    """
    import rich
    from rich.panel import Panel

    rich.print(Panel(f"{a = }, {b = }, {c = }", width=DEFAULT_CONSOLE_OUTPUT_WIDTH))


@exec_task(immediate_run=True)
def return_arguments_as_string(a: int = 42, b: float = 3.14, c: str = "default") -> str:
    """
    This task will run immediately when pressed. The parameters will always have
    the default arguments. No output is printed, the task returns a string
    representing the default arguments.
    """
    return f"{a = }, {b = }, {c = }"


@exec_task(immediate_run=True)
def return_arguments_as_tuple(a: int = 42, b: float = 3.14, c: str = "default") -> tuple:
    """
    This task will run immediately when pressed. The parameters will always have
    the default arguments. No output is printed, the task returns a tuple with
    each of the parameters and their default argument.
    """
    return a, b, c
