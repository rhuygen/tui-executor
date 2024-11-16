"""
The purpose of this module is to demonstrate function names and display names.
The function name will be cut short at 32 characters (defined by the constant
MAX_WIDTH_FUNCTION_NAME). This is only for keeping the display properly
aligned.

You can always use the display_name to use instead of the function name in the
task button.
"""
from tui_executor import MAX_WIDTH_FUNCTION_NAME
from tui_executor.exec import exec_task


@exec_task()
def function_with_a_long_name():
    """
    The length of the function name should still fit the space allowed in the
    task buttons panel.
    """
    print(f"The filename is 25 characters long. The maximum allowed length is {MAX_WIDTH_FUNCTION_NAME}")


@exec_task()
def function_with_an_extra_log_name():
    """
    The length of the function name will fit the space that is allowed in the
    task buttons panel because it's not an immediate_run task and therefore
    doesn't have the triangles ▶ <function name> ◀.
    """
    print(f"The filename is 31 characters long. The maximum allowed length is {MAX_WIDTH_FUNCTION_NAME}")


@exec_task(display_name="Just a function")
def another_function_with_an_extra_long_name():
    """
    The length of the function name will not fit the space that is allowed in
    the task buttons panel, but we used a display_name to fix that.
    """
    print(
        f"The filename is 40 characters long. "
        f"The maximum allowed length is {MAX_WIDTH_FUNCTION_NAME}\n"
        f"You will not see the function name in the task button, because we defined a display_name."
    )


@exec_task(immediate_run=True)
def a_function_with_an_extra_and_too_log_name():
    """
    The length of the function name will not fit the space that is allowed in
    the task buttons panel because it is an immediate_run task and therefore
    will have the triangles around its name ▶ <function name> ◀.
    """
    print(f"The filename is 41 characters long. The maximum allowed length is {MAX_WIDTH_FUNCTION_NAME}")
