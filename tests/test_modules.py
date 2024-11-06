import sys
from pathlib import Path

import rich

from tui_executor.modules import find_modules
from tui_executor.modules import find_subpackages
from tui_executor.modules import get_module_location
from tui_executor.modules import get_script_module
from tui_executor.modules import get_ui_modules
from tui_executor.modules import get_ui_subpackages

HERE = Path(__file__).parent.resolve()


def test_find_modules():

    rich.print()

    mods = find_modules("tasks.shared")
    rich.print(mods)
    assert mods == {}

    mods = find_modules("tasks.shared.unit_tests")
    rich.print(mods)
    assert "recurring_tasks" in mods
    assert mods["recurring_tasks"] == 'tasks.shared.unit_tests.recurring_tasks'
    assert "input_requests" in mods
    assert mods["input_requests"] == "tasks.shared.unit_tests.input_requests"


def test_find_subpackages():

    rich.print()

    subpkgs = find_subpackages("tasks")
    rich.print(subpkgs)
    assert "specific" in subpkgs
    assert isinstance(subpkgs["specific"], Path)
    assert str(subpkgs["specific"]).endswith("tasks/specific")
    assert subpkgs["specific"].is_dir()

    subpkgs = find_subpackages("tasks.specific")
    rich.print(subpkgs)
    assert "errors" in subpkgs
    assert str(subpkgs["errors"]).endswith("tasks/specific/errors")
    assert subpkgs["errors"].is_dir()

    subpkgs = find_subpackages("tasks.specific.errors")
    rich.print(subpkgs)
    assert subpkgs == {}


def test_get_module_location():

    rich.print()

    rich.print(f"{sys.path = }")

    all_module_paths = [
        # (module path, expected location)
        ("tasks", HERE / "tasks"),  # will print a warning for namespace package
        ("tasks.shared", HERE / "tasks/shared"),
        ("tasks.shared.unit_tests", HERE / "tasks/shared/unit_tests"),
        ("tasks.shared.unit_tests.immediate_run", HERE / "tasks/shared/unit_tests"),
    ]

    for module_path, expected in all_module_paths:
        location = get_module_location(module_path)
        rich.print(f"{location = }")
        assert location == expected


def test_get_ui_modules():

    rich.print()

    rich.print(f"{sys.path = }")

    module_path = "tasks.shared.unit_tests"
    ui_mods = get_ui_modules(module_path)
    rich.print(f"{module_path = }, {ui_mods = }")
    assert "immediate_run" in ui_mods
    assert ui_mods["immediate_run"] == ('immediate_run', 'tasks.shared.unit_tests.immediate_run')
    assert "recurring_tasks" in ui_mods
    assert ui_mods["recurring_tasks"] == ('01 - Recurring Tasks', 'tasks.shared.unit_tests.recurring_tasks')

    module_path = "tasks.specific"
    ui_mods = get_ui_modules(module_path)
    rich.print(f"{module_path = }, {ui_mods = }")
    assert "recurring" in ui_mods
    assert ui_mods["recurring"] == ('recurring', 'tasks.specific.recurring')

    module_path = "tasks.specific.input_fields"
    ui_mods = get_ui_modules(module_path)
    rich.print(f"{module_path = }, {ui_mods = }")
    assert "simple" in ui_mods
    assert ui_mods["simple"] == ('simple', 'tasks.specific.input_fields.simple')
    assert "var_name" in ui_mods
    assert ui_mods["var_name"] == ('Passing known variables', 'tasks.specific.input_fields.var_name')


def test_get_ui_subpackages():

    rich.print()

    module_path = "tasks.shared"
    ui_subpkgs = get_ui_subpackages(module_path)
    rich.print(ui_subpkgs)
    assert "unit_tests" in ui_subpkgs
    assert ui_subpkgs["unit_tests"][0] == 'Unit Tests'
    assert str(ui_subpkgs["unit_tests"][1]).endswith("shared/unit_tests")
    assert ui_subpkgs["unit_tests"][1].is_dir()

    module_path = "tasks.specific"
    ui_subpkgs = get_ui_subpackages(module_path)
    rich.print(ui_subpkgs)


def test_get_script_module():

    rich.print()

    script = get_script_module(HERE / 'scripts/print_sys_path.py')

    rich.print(script)
