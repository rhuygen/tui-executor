"""
This module provides functions to find modules and (sub-)packages given a module path or a location.

Note the difference between a module path and a location:

- module_path: a string that defines the dotted module path of a package or module, e.g. 'pkg.subpkg.mod'.
- location: a string or a Path pointing to a relative or absolute file path, e.g. 'tasks/shared/unit_tests'.
"""
from __future__ import annotations

__all__ = [
    "find_modules",
    "find_subpackages",
    "get_module_location",
    "get_script_module",
    "get_ui_modules",
    "get_ui_subpackages",
]

import importlib
import textwrap
import warnings
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple

from textual import log


def find_subpackages(module_path: str) -> Dict[str, Path]:
    """
    Finds Python sub-packages in the given module path. A sub-package is a folder below the location of the
    module_path's location and shall contain an '__init__.py' file. The search for sub-packages is non-recursive.

    Args:
        module_path: the module path where the Python modules and scripts are located, e.g. `pkg.subpkg`

    Returns:
        A dictionary with the subpackage names as keys and their paths as values.
    """
    location = get_module_location(module_path)

    return {item.name: item for item in location.iterdir() if item.is_dir() and (item / "__init__.py").exists()}


def find_modules(module_path: str) -> Dict[str, str]:
    """
    Finds Python modules and scripts in the given module path (non recursively). The modules will not be
    imported, instead their dotted module path will be returned. The idea is that the caller can decide which
    modules to import. The search for modules is non-recursive.

    Args:
        module_path: the module path where the Python modules and scripts are located, e.g. `pkg.subpkg`

    Returns:
        A dictionary with module name as keys and their dotted module path as values.
    """
    location = get_module_location(module_path)

    return {
        item.stem: f"{module_path}.{item.stem}"
        for item in location.glob("*.py")
        if item.name not in ["__init__.py"]
    }


def get_module_location(module_path: str) -> Path:
    """
    Returns the Path where a module is located. If the module is a folder, that folder name will be returned, If the
    module is a '*.py' file, the folder where that module is located will be returned.

    Args:
        module_path: the full path of a module, e.g. `pkg.subpkg`, `pkg.mod`, `pkg.subpkg.mod`

    A Warning will be shown when the module path is pointing to a namespace package.
    """
    mod = importlib.import_module(module_path)

    if hasattr(mod, "__path__") and getattr(mod, "__file__", None) is None:
        warnings.warn(
            textwrap.dedent(f"""
                The module '{mod.__name__}' is a namespace package, i.e. a package without an '__init__.py' file.
                Please, properly define your module and add an '__init__.py' file. The file can be empty.
                Your package is located at {set(mod.__path__)}.
                """)
        )

        paths: List[str] = list(set(mod.__path__))
        location = Path(paths[0])
    else:
        location = Path(mod.__file__).parent

    if not location.is_dir():
        raise ValueError(f"Expected a folder, instead got {str(location)}")

    return location


def get_script_module(script_location: Path | str, exec_module: bool = False) -> Dict[str, Any]:
    """
    Locate the given scripts and return it as a module.

    If the scripts_location argument is a relative pathname, it will be searched from the working directory, otherwise
    provide an absolute filename.

    Args:
        script_location: filename of the script
        exec_module: execute the script using its source file loader

    Returns:
        A dictionary with the script's filename without extension as the key and the script as a module as the value.
    """
    script_path = Path(script_location).resolve()

    loader = importlib.machinery.SourceFileLoader(script_path.stem, str(script_path))
    spec = importlib.util.spec_from_loader(script_path.stem, loader)
    script = importlib.util.module_from_spec(spec)

    if exec_module:
        loader.exec_module(script)

    return {script_path.stem: script}


def get_ui_modules(module_path: str) -> Dict[str, Tuple[str, str]]:
    """
    Find all modules in the given module path. A module is a Python file (`*.py`),
    not a directory. The search for modules is non-recursive.

    All modules will be imported. That will reveal any import error and is also
    needed to get the value of the display name of the module, in `UI_MODULE_DISPLAY_NAME`.

    Args:
        module_path: a full dotted module path, e.g. 'tasks.shared'.

    Returns:
        A dictionary with module name as key and where the value is
        a tuple (display name, dotted module path).

    Logs:
        When an exception is raised during import, the exception is logged as
        a warning.
    """
    response = {}

    for name, dotted_path in find_modules(module_path).items():
        try:
            mod = importlib.import_module(dotted_path)
            display_name = getattr(mod, "UI_MODULE_DISPLAY_NAME", name)
            response[name] = (display_name, dotted_path)
        except Exception as exc:
            log.warning(f"{exc.__class__.__name__}: {exc} ({dotted_path})")

    return response


def get_ui_subpackages(module_path: str) -> Dict[str, Tuple[str, Path]]:
    """
    Returns all sub-packages for the given module path. The function does not
    search for sub-packages recursively. Sub-packages that have the variable
    'UI_TAB_HIDE' defined will be omitted when the function associated with
    that variable returns True.

    Args:
        module_path: the full dotted module path, e.g. 'tasks.shared'.

    Returns:
        A dictionary with the module name as key and where the value is a tuple
        (tab name, package directory path).
    """
    response = {}

    for name, path in find_subpackages(module_path).items():
        mod = importlib.import_module(f"{module_path}.{name}")

        # If the module contains a variable UI_TAB_HIDE that is a Callable (function),
        # execute the function to determine if the module shall be included or not.

        hide_tab = getattr(mod, 'UI_TAB_HIDE', None)
        if isinstance(hide_tab, Callable) and hide_tab():
            continue

        display_name = getattr(mod, "UI_TAB_DISPLAY_NAME", name)
        response[name] = (display_name, path)

    return response
