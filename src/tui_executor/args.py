__all__ = [
    "get_arguments",
    "Directory",
    "FileName",
    "FilePath",
]

import inspect
from enum import IntEnum
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import TypeVar

"""
The following TypeVars can be used to distinguish between a file and a folder when annotating a function
argument as a Path. The GUI can make the distinction as follows, based on the annotation:

    def func(x: FileName):
        ...

    sig = inspect.signature(func)
    pars = sig.parameters
    par_x = pars['x']
    par_x.annotation is Filename  <-- True

"""

FileName = TypeVar('FileName', bound=Path)
"""A FileName type is the name of a file including the extension, but not it's full path."""
FilePath = TypeVar('FilePath', bound=Path)
"""A FilePath is the absolute or relative path for a file, including filename and extension."""
Directory = TypeVar('Directory', bound=Path)
"""A Directory is the location where the file resides."""


class ArgumentKind(IntEnum):
    POSITIONAL_ONLY = 0
    POSITIONAL_OR_KEYWORD = 1
    VAR_POSITIONAL = 2
    KEYWORD_ONLY = 3
    VAR_KEYWORD = 4


class Argument:
    def __init__(self, name: str, kind: int, annotation: Any, default: Any):
        self.name = name
        self.kind: ArgumentKind = ArgumentKind(kind)
        self.annotation = annotation
        self.default = default


# Why I use my own class Arguments instead of just inspect.Parameter?
# * because I don't want to be dependent on inspect.Parameter.empty in my apps
# * because Argument might get more info from the exec_ui decorator, like e.g. units
#   or a description of the argument.

# Maybe I should use a Sentinel object instead of None when inspect.Parameter.empty?

def get_arguments(func: Callable) -> Dict[str, Argument]:
    """
    Determines the signature of the function and returns a dictionary with keys the name of the arguments
    and values the Argument object for the arguments.

    Args:
        func: a function callable

    Returns:
        A dictionary with all arguments.
    """
    sig = inspect.signature(func)
    pars = sig.parameters
    return {
        k: Argument(
            k,
            int(v.kind),
            None if v.annotation == inspect.Parameter.empty else v.annotation,
            None if v.default == inspect.Parameter.empty else v.default
        )
        for k, v in pars.items()
    }
