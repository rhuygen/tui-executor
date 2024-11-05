from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from tui_executor.exec import exec_task
from tui_executor.exec import exec_ui
from tui_executor.funcpars import Empty
from tui_executor.funcpars import ParameterKind
from tui_executor.funcpars import get_parameters
from tui_executor.functions import find_ui_button_functions
from tui_executor.functions import find_ui_functions
from tui_executor.modules import find_modules
from tui_executor.tasks import TaskKind
from tui_executor.utils import sys_path

HERE = Path(__file__).parent.resolve()


def test_exec_ui():

    @exec_ui(description="Press and get Pressed.")
    def press():
        return "Pressed"

    assert hasattr(press, "__ui_kind__")
    assert press.__ui_kind__ == TaskKind.BUTTON
    assert press.__ui_description__ == "Press and get Pressed."
    assert press() == "Pressed"


def test_exec_task():

    @exec_task(description="Press and get Pressed.")
    def press():
        return "Pressed"

    assert hasattr(press, "__ui_kind__")
    assert press.__ui_kind__ == TaskKind.BUTTON
    assert press.__ui_description__ == "Press and get Pressed."
    assert press() == "Pressed"


def test_find_modules():
    print()
    with sys_path(HERE):  # make sure Python knows where to look for the module
        scripts = find_modules("scripts")

    assert "define_some_globals" in scripts

    define_some_globals = importlib.import_module(scripts["define_some_globals"])

    assert define_some_globals.EXEC_SCRIPT

    funcs = find_ui_functions(scripts["define_some_globals"])

    assert "echo" not in funcs
    assert "ui_echo" in funcs
    assert "hello, World!" in funcs["ui_echo"]("hello, World!")

    with sys_path(HERE):  # make sure Python knows where to look for the module
        mods = find_modules("tasks.shared.unit_tests")

    print(f"from tasks, {mods = }")

    assert "__init__" not in mods
    assert "ui_test_script" in mods

    mod = importlib.import_module(mods["ui_test_script"])
    assert mod.__name__ == "tasks.shared.unit_tests.ui_test_script"


def test_find_sub_modules():

    print()

    with sys_path(HERE):
        tasks = find_modules("tasks")

    print(tasks)


def test_ui_script():

    with sys_path(HERE):  # make sure Python knows where to look for the module
        funcs = find_ui_button_functions("tasks.shared.unit_tests.ui_test_script")

    assert "concatenate_args" in funcs
    assert "compare_args" in funcs

    concatenate_args = funcs["concatenate_args"]
    assert concatenate_args("one", "two") == "onetwo"
    assert concatenate_args.__doc__ == "Concatenates the two arguments with the '+' operator."

    compare_args = funcs["compare_args"]
    assert not compare_args(23, "two")
    assert compare_args(42, 42)
    assert compare_args.__doc__ == "Compares the two arguments with the '==' operator."


def test_ui_function_args():

    print()

    # This test is here only to learn about how to interpret the Signatures

    with sys_path(HERE):  # make sure Python knows where to look for the module
        funcs = find_ui_button_functions("tasks.shared.unit_tests.ui_test_script")

    func = funcs["func_with_args"]
    sig = inspect.signature(func)
    pars = sig.parameters

    assert 'x' in pars
    assert pars['x'].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert 'y' in pars

    func = funcs["func_with_only_kwargs"]
    sig = inspect.signature(func)
    pars = sig.parameters

    print(f"{pars = }")
    print([p for p in pars.items()])

    assert 'a' in pars
    assert pars['a'].kind == inspect.Parameter.KEYWORD_ONLY
    assert 'b' in pars
    assert pars['b'].kind == inspect.Parameter.KEYWORD_ONLY

    assert pars['a'].annotation == str
    assert pars['a'].default == inspect.Parameter.empty

    assert pars['b'].annotation == int
    assert pars['b'].default == 42

    print(f"{pars['b'] = }")


def test_get_parameters():

    print()

    with sys_path(HERE):  # make sure Python knows where to look for the module
        funcs = find_ui_button_functions("tasks.shared.unit_tests.ui_test_script")

    func = funcs["func_with_only_kwargs"]

    args = get_parameters(func)

    arg_a = args["a"]
    print(f"{arg_a.annotation = }")
    print(f"{arg_a.default = }")
    assert arg_a.name == 'a'
    assert arg_a.kind == ParameterKind.KEYWORD_ONLY
    assert arg_a.annotation == str
    assert arg_a.default == Empty

    arg_b = args["b"]
    print(f"{arg_b.annotation = }")
    print(f"{arg_b.default = }")
    assert arg_b.name == 'b'
    assert arg_b.kind == ParameterKind.KEYWORD_ONLY
    assert arg_b.annotation == int
    assert arg_b.default == 42

    arg_c = args['c']

    assert arg_c.name == 'c'
    print(f"{arg_c.annotation = }")
    print(f"{arg_c.default = }")
    assert arg_c.kind == ParameterKind.KEYWORD_ONLY
    assert arg_c.annotation is Empty
    assert arg_c.default is Empty
