import textwrap
import time

import pytest

from tui_executor.client import MyClient
from tui_executor.kernel import MyKernel


@pytest.fixture(scope="module")
def kernel():
    kernel = MyKernel()

    yield kernel

    del kernel  # explicitly shutdown the kernel


@pytest.mark.order(1)
def test_kernel_initialisation(kernel):

    snippet = textwrap.dedent("""\
        a = 42
        print(f"{a = }")
        for _ in range(5):
            a += 2
            print(f"{a = }")
        print(f"total = {a}")
    """)

    with MyClient(kernel) as client:
        out = client.run_snippet(snippet)

    print()
    print(f"*****\n{out}\n*****")

    assert "a = 44" in out
    assert "a = 52" in out
    assert "total = 52" in out


@pytest.mark.order(2)
def test_kernel_after_initialisation(kernel):

    with MyClient(kernel) as client:

        out = client.run_snippet("""print(f"{a = }")""")

        print()
        print(f"*****\n{out}\n*****")

        assert "a = 52" in out

        out = client.run_snippet("""print(a is not None)""")

        print()
        print(f"*****\n{out}\n*****")

        assert out == "True"

        out = client.run_snippet("""a is not None""")

        print()
        print(f"*****\n{out}\n*****")

        # assert out == "True"  # no output expected as there is no print function called


def test_kernel_info(kernel):

    import rich

    rich.print()

    with MyClient(kernel) as client:
        info = client.get_kernel_info()
        rich.print("Kernel Info")
        rich.print(info)


@pytest.mark.asyncio
async def test_run_snippet(kernel):

    print()

    snippet = textwrap.dedent(
        """
        import time

        print("starting...", flush=True, end="")
        time.sleep(5.0)
        print("finished!", flush=True)

    """)

    with MyClient(kernel) as client:
        msg_id = client.execute(snippet)

        msg = client.get_shell_msg(msg_id)
        print(f"1 {'-' * 20} {msg = }")

        io_msg = client.get_iopub_msg(timeout=1.0)
        io_msg_content = io_msg['content']
        print(f"2 {'-' * 20} {io_msg_content = }")

        time.sleep(5.0)

        io_msg = client.get_iopub_msg(timeout=1.0)
        io_msg_content = io_msg['content']
        print(f"3 {'-' * 20} {io_msg_content = }")

        io_msg = client.get_iopub_msg(timeout=1.0)
        io_msg_content = io_msg['content']
        print(f"4 {'-' * 20} {io_msg_content = }")

        io_msg = client.get_iopub_msg(timeout=1.0)
        io_msg_content = io_msg['content']
        print(f"5 {'-' * 20} {io_msg_content = }")

        io_msg = client.get_iopub_msg(timeout=1.0)
        io_msg_content = io_msg['content']
        print(f"6 {'-' * 20} {io_msg_content = }")
