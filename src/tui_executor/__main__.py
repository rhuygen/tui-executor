import argparse
import logging
import sys
from pathlib import Path

from tui_executor.app import TuiExecutorApp
from tui_executor.utils import print_system_info
from tui_executor.version import __version__ as version

HERE = Path(__file__).parent.resolve()


def main():

    parser = argparse.ArgumentParser(prog='tui-executor')
    parser.add_argument('--version', "-V", action="store_true", help='print the tui-executor version number and exit')
    parser.add_argument('--verbose', "-v", action="count",
                        help="print verbose information, increased verbosity level with multiple occurrences")
    parser.add_argument('--cmd-log', help='location of the command log files')
    parser.add_argument('--module-path', action="append", help='module path of the Python modules and scripts')
    parser.add_argument('--kernel-name',
                        help="the kernel that will be started by default, python3 if not given")
    parser.add_argument('--app-name', help='the name of the TUI app, will go in the window title')
    parser.add_argument('--debug', '-d', action="store_true", help="set debugging mode")
    parser.add_argument('--single', action="store_true",
                        help='the UI can be started only once (instead of multiple times)')

    args = parser.parse_args()

    verbosity = 0 if args.verbose is None else args.verbose
    kernel_name = args.kernel_name or "python3"
    app_name = args.app_name or "TUI Executor"
    module_path_list = args.module_path

    single = 1 if args.single is None else args.single
    lock_file = None

    if args.version:
        print(f"tui-executor {version=}")
        if verbosity:
            print_system_info()
        sys.exit(0)

    log = logging.getLogger('tui-executor')
    log.setLevel(logging.DEBUG if args.debug else logging.WARNING)

    # We have only implemented the --module-path option for now

    if args.module_path is None:
        print("You need to provide at least one --module-path option.")
        parser.print_help()
        return

    if args.cmd_log and not Path(args.cmd_log).exists():
        print("The argument to --cmd-log must be an existing directory.")
        parser.print_help()
        return

    app = TuiExecutorApp(module_path_list=args.module_path)

    if not single:
        return app.run()
    else:
        error_message = f"The {args.app_name or 'TUI Executor'} application is already running!"
        return error_message


if __name__ == "__main__":
    main()
