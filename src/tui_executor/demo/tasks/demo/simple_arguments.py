from tui_executor.exec import exec_task


@exec_task()
def one_bool(value: bool):
    """
    This task accept a bool argument and returns that argument without
    processing. No default is provided.
    """
    return value


@exec_task()
def one_bool_with_default(value: bool = True):
    """
    This task accept a bool argument and returns that argument without
    processing. The argument is True by default.
    """
    return value


@exec_task(display_name="Two integers")
def two_integers(a: int, b: int):
    return a, b


@exec_task(display_name="Two integers, one default")
def two_integers_one_default(a: int, b: int = 42):
    return a, b
