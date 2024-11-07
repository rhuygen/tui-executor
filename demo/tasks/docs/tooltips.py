"""
This module demonstrates how docstrings are translated into tooltips in the
`tui-executor` app. The module docstrings are used as a tooltip when you
hover over the title of the collapsible sections, while the function
docstrings are used as tooltips for the task buttons.
"""
from tui_executor.exec import exec_task


@exec_task(display_name="Tooltip Example")
def example(name: str, count: int, timeout: float = 60.0):
    """
    This is an example function with a proper docstring that will be shown as a
    tooltip. The Tooltip widget is styled with a maximum width of 80 characters,
    so make sure the paragraphs here are not wider than 80 characters.

    You can use [red]styles[/] like [b]bold[/] or [i]italic[/] to emphasize parts of the docstring.

    Args:
        name (str): in the name of love
        count (int): number of times to run the examples
        timeout (float): if execution takes longer than the given timeout, abort
            and send a log warning message. \[default is 60.0s].

    Returns:
        This function always returns True, unless there was a timeout, then
        False is returned.
    """
    return True
