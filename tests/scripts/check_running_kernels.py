import logging
import textwrap

import rich

from tui_executor.client import MyClient
from tui_executor.kernel import MyKernel
from tui_executor.kernel import find_running_kernels

logging.basicConfig(level=logging.INFO)


def main():

    my_kernel = MyKernel()

    for kernel in find_running_kernels():
        rich.print(f"kernel.get_connection_info() = ", kernel.get_connection_info(), end='')
        rich.print(f"{kernel.get_connection_file() = }")
        rich.print(f"{kernel.get_pid() = }")
        rich.print(f"{kernel.get_kernel_type() = }")
        rich.print(f"kernel.get_kernel_specs() = ", kernel.get_kernel_specs(), end='')
        rich.print(f"{kernel.get_client() = }")
        rich.print(f"{kernel.is_alive() = }")

        kernel_info = kernel.get_kernel_info()
        rich.print(f"{kernel_info = }")
        rich.print(f"{kernel_info.creation_datetime = }")
        rich.print(f"{kernel_info.kernel = }")

        with kernel.get_client() as client:
            cmd, out, err = client.run_snippet(snippet='a = 42')
            print_cmd_out_err(cmd, out, err)

        with MyClient(kernel) as client:
            cmd, out, err = client.run_snippet(snippet='print("Hello, World!")')
            print_cmd_out_err(cmd, out, err)
            cmd, out, err = client.run_snippet(snippet='from camtest.version import VERSION')
            print_cmd_out_err(cmd, out, err)
            # rich.print(f"error = \n{client.get_error()}")
            cmd, out, err = client.run_snippet(snippet='print(VERSION)')
            print_cmd_out_err(cmd, out, err)
            cmd, out, err = client.run_snippet(snippet='print(f"{a = }")')
            print_cmd_out_err(cmd, out, err)

            cmd, out, err = client.run_snippet(
                snippet=textwrap.dedent(
                    """\
                    print(f"{a = }")
                    
                    for _ in range(3):
                        print(_)
                    """
                )
            )
            print_cmd_out_err(cmd, out, err)

            rich.print(f"client.get_kernel_info() = ", client.get_kernel_info())

        # The following statement will not shut down the kernel, since the kernel
        # object was created using the process ID in `find_running_kernels()`.

        kernel.shutdown()

    my_kernel.shutdown()

    input("<Press any key to finish this test>")
    rich.print(f"{my_kernel.is_alive() = }")


def print_cmd_out_err(cmd, out, err):
    if len(cmd) > 1:
        cmd = '\n'.join(cmd)
        rich.print(f"[red]cmd = [/]\n{cmd}")
    else:
        rich.print(f"[red]cmd = [/] = {cmd}")

    if len(out) > 1:
        out = '\n'.join(out)
        rich.print(f"out = \n{out}")
    else:
        rich.print(f"{out = }")

    if err:
        err = '\n'.join(err)
        rich.print(f"err = \n{err}")


if __name__ == "__main__":
    main()
