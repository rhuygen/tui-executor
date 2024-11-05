"""
This module works with function parameters. It provides a function to retrieve the parameter definitions of a given
function callable and defines a number of parameter types that can be used to distinguish between filenames, paths,
and folders.

Please note the importance of naming:

- a `parameter` is a variable inside the parentheses in the function definition.
- an `argument` is the value that is sent when calling the function.

"""
__all__ = [
    "Directory",
    "Empty",
    "FileName",
    "FilePath",
    "Parameter",
    "ParameterKind",
    "get_parameters",
]

import inspect
from enum import IntEnum
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import TypeVar

from tui_executor.utils import Singleton

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


class ParameterKind(IntEnum):
    """The kind of parameter for a function, e.g. positional, keyword, ..."""
    POSITIONAL_ONLY = 0
    POSITIONAL_OR_KEYWORD = 1
    VAR_POSITIONAL = 2
    KEYWORD_ONLY = 3
    VAR_KEYWORD = 4


# Why I use my own class Parameter instead of just inspect.Parameter?
# * because I don't want to be dependent on inspect.Parameter.empty in my apps,
#   I use a Sentinel object instead of None when inspect.Parameter.empty.
# * because Parameter might get more info from the `exec_task` decorator,
#   like e.g. units or a description of the argument.


class Parameter:
    """
    The parameter of a function, i.e. the variable inside the parentheses in the function definition.

    Note this is the definition of the parameter while the value that is sent when calling the function
    is called the argument.

    Every Parameter has a name, a kind (positional, keyword, ...), an annotation and a default value.

    Args:
         name: the name of the parameter
         kind: the kind of parameter, i.e. positional, keyword, ... (See the ParameterKind enum)
         annotation: an annotation for the Parameter or None
         default: a default value or None
    """
    def __init__(self, name: str, kind: int, annotation: Any, default: Any):
        self.name = name
        self.kind: ParameterKind = ParameterKind(kind)
        self.annotation = annotation
        self.default = default


class Empty(Singleton):
    """A marker object for the Signature and Parameters that have no annotation nor a default value."""


def get_parameters(func: Callable) -> Dict[str, Parameter]:
    """
    Determines the signature of the function and returns a dictionary with as keys the name of the parameters
    and as values the parameter definition for all parameters in this function definition.

    Args:
        func: a function callable

    Returns:
        A dictionary with all parameters.
    """
    sig = inspect.signature(func)
    pars = sig.parameters
    return {
        k: Parameter(
            k,
            int(v.kind),
            Empty if v.annotation == inspect.Parameter.empty else v.annotation,
            Empty if v.default == inspect.Parameter.empty else v.default
        )
        for k, v in pars.items()
    }
