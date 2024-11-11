import rich

from tui_executor.kernel import MyKernel
from tui_executor.kernel import start_qtconsole


def main():

    kernel = MyKernel()

    try:
        ext_cmd = start_qtconsole(kernel)

        while ext_cmd.is_running:
            pass

        if ext_cmd.stderr:
            rich.print(ext_cmd.stderr.decode())

    except ChildProcessError as exc:
        rich.print(f"[red]Caught ChildProcessError:[/] {exc}")
    except KeyboardInterrupt:
        rich.print("[red]Caught KeyboardInterrupt, terminating...[/]")


if __name__ == '__main__':
    main()
