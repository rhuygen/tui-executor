import time

import rich

from tui_executor.exec import exec_task


@exec_task(display_name="Sleeping")
def just_sleep(duration: float = 10.0):
    """Just sleep for the given number of seconds, default is 10 seconds."""

    time.sleep(duration)


@exec_task(display_name="Intermediate Output", immediate_run=True)
def intermediate_output():
    """
    This script runs for half a minute with intermediate output that should show
    up in the Output Console. The output is expected to appear during the
    execution of the task. There will be an elapsed time report every second.
    """

    period = 1.0  # do every second

    def g_tick():
        next_time = time.time()
        while True:
            next_time += period
            yield max(next_time - time.time(), 0)

    start_time = time.monotonic()

    g = g_tick()
    while (elapsed_time := time.monotonic() - start_time) < 30.0:
        rich.print(f"time elapsed: {elapsed_time:.3f}s")
        time.sleep(next(g))
