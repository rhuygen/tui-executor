import logging
import textwrap
import time

import rich
from rich.console import Console

from tui_executor.kernel import MyKernel


def do_test_my_kernel(name: str = "python3", pid: int = 0):
    from tui_executor.client import MyClient
    from tui_executor.utils import Timer

    if pid > 0:
        kernel = MyKernel(pid=pid)
    else:
        kernel = MyKernel(name=name)

    rich.print(kernel.get_kernel_specs())
    rich.print(f"{kernel.is_alive() = }")

    client = MyClient(kernel)
    client.connect()

    rich.print(client.get_kernel_info())

    snippets = [
        "a=2",
        textwrap.dedent("""\
            a = 42
            b = 73
            c = a + b
            print(c)        
            """),
        'print(f"{a=}, {b=}, {c=}")',
        '1/0',  # should return a ZeroDivisionError
        'import sys; print(f"{sys.path = }")',
        'import pandas as pd',
        'df = pd.DataFrame(dict(A=[1,2,3], B=["one", "two", "three"]))',
        'print(df)',
        'print(df.describe())',
    ]

    console = Console(width=240)
    for n, snippet in enumerate(snippets):
        with Timer(f"cmd — snippet {n}"):
            response = client.run_snippet(snippet)
        if response:
            cmd, out, err = response
            if cmd:
                end = '\n' if len(cmd) > 1 else ''
                console.print("[blue]cmd: [/]", end=end)
                console.print('\n'.join(cmd))
            if out:
                end = '\n' if len(out) > 1 else ''
                console.print("[green]out: [/]", end=end)
                console.print('\n'.join(out))
            elif err:
                end = '\n' if len(out) > 1 else ''
                console.print("[red]err: [/]", end=end)
                console.print('\n'.join(err))

    client.disconnect()

    with Timer("MyClient as context manager"):
        with MyClient(kernel) as client:
            info = client.get_kernel_info()

    # while True:
    #     time.sleep(1.0)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    # kernel_name = "python3"
    # kernel_name = "plato-common-egse"
    kernel_name = "plato-test-scripts"

    # do_test_my_kernel(pid=92528)
    do_test_my_kernel(name=kernel_name)
