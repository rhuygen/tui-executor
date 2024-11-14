from tui_executor.exec import exec_task
from tui_executor.utils import format_datetime


@exec_task(immediate_run=True)
def now():
    """Return the current datetime in UTC."""

    return format_datetime()
