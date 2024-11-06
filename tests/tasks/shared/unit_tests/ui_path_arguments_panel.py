from pathlib import Path

from tui_executor.exec import exec_ui
from tui_executor.funcpars import Directory
from tui_executor.funcpars import FileName
from tui_executor.funcpars import FilePath

UI_MODULE_DISPLAY_NAME = "Path-like Arguments"


@exec_ui(display_name="Select a folder")
def select_folder(location: Path):
    print(f"{location = }")


@exec_ui(display_name="Open File")
def open_file(
        filename: FileName = "README.md",
        filepath: FilePath = None,
        location: Directory = Path("/Users/rik/Documents/PyCharmProjects/gui-executor/"),
):
    print(f"{filename = }, {type(filename) = }")
    print(f"{filepath = }, {type(filepath) = }")
    print(f"{location = }, {type(location) = }")
