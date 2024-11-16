import sys
import time

from tui_executor.exec import exec_ui


@exec_ui(immediate_run=True)
def raise_a_value_error():
    """This function just raises a ValueError after it first sleeps for 1s."""
    print("This function will raise a ValueError after 1s...", flush=True)
    print("This message is sent to stderr.", file=sys.stderr)

    time.sleep(1.0)

    raise ValueError("Exception raised as an example..")


@exec_ui(immediate_run=True)
def return_a_value_error() -> Exception:
    """
    This task raises a ValueError, but instead of handling or raising the
    caught exception, it will return the exception object. As you will see,
    the message of the exception will be printed in the output console, but
    not the exception itself. That is because the kernel will return the
    message as plain text, and will not generate a `Traceback` for it.
    """
    try:
        raise ValueError("Value Error not raised, but returned.")
    except Exception as exc:
        return exc
