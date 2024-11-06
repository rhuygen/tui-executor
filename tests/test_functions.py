import inspect

import rich

from tui_executor.functions import find_ui_functions
from tui_executor.functions import get_ui_button_functions
from tui_executor.functions import get_ui_recurring_functions


def test_find_ui_functions():
    rich.print()

    funcs = find_ui_functions("tasks")
    rich.print(funcs)
    assert funcs == {}

    funcs = find_ui_functions("tasks.shared")
    rich.print(funcs)
    assert funcs == {}

    funcs = find_ui_functions("tasks.shared.unit_tests")
    rich.print(funcs)
    assert funcs == {}

    funcs = find_ui_functions("tasks.shared.unit_tests.immediate_run")
    rich.print(funcs)
    assert "stop_hexapod" in funcs
    assert inspect.isfunction(funcs["stop_hexapod"])


def test_get_ui_button_functions():

    rich.print()

    funcs = get_ui_button_functions("tasks.specific.output.renderable")
    rich.print(funcs)
    assert "renderable_output" in funcs
    assert "normal_function" not in funcs


def test_get_ui_recurring_functions():

    rich.print()

    funcs = get_ui_recurring_functions("tasks.specific.recurring")
    rich.print(funcs)
    assert "sleep_1s" in funcs
    assert inspect.isfunction(funcs["sleep_1s"])
