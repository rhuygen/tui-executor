import platform
import textwrap
from pathlib import Path

import textual

from tui_executor.exec import exec_task
from tui_executor.version import get_version

HERE = Path(__file__).parent.resolve()
ICON_PATH = HERE / "../../../../src/tui_executor/icons/"


@exec_task(immediate_run=True)
def print_sys_path():
    """Print the `sys.path` for the running kernel."""

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
def return_arguments_as_string(a: int = 42, b: float = 3.14, c: str = "default") -> str:
    """Return the arguments as one string."""
    return f"{a = }, {b = }, {c = }"


@exec_task(immediate_run=True)
def return_arguments_as_tuple(a: int = 42, b: float = 3.14, c: str = "default") -> tuple:
    """Returns the arguments as a tuple with three elements, a, b, and c."""
    return a, b, c
