from pathlib import Path

from tui_executor.exec import exec_task

HERE = Path(__file__).parent.resolve()
ICON_PATH = HERE / "../../../../src/tui_executor/icons/"


@exec_task(immediate_run=True, icons=(ICON_PATH / "stop.svg", ICON_PATH / "stop.svg"))
def stop_immediately():
    import rich
    from rich.panel import Panel

    rich.print(Panel("Pressed the [red]STOP[/] button!"))


@exec_task(immediate_run=True)
def return_arguments_as_string(a: int = 42, b: float = 3.14, c: str = "default") -> str:

    return f"{a = }, {b = }, {c = }"


@exec_task(immediate_run=True)
def return_arguments_as_tuple(a: int = 42, b: float = 3.14, c: str = "default") -> tuple:

    return a, b, c
