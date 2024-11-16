from __future__ import annotations

__all__ = [
    "KernelInfo",
    "MyKernel",
    "find_kernel_processes",
    "find_running_kernels",
    "get_connection_file",
    "get_connection_info",
    "get_key",
    "start_kernel",
]

import datetime
import json
import logging
import os
import re
import textwrap
import warnings
from importlib.util import find_spec
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import Iterator

import jupyter_client.kernelspec
import psutil
from executor import ExternalCommand
from executor import ExternalCommandFailed
from jupyter_client.manager import KernelManager
from rich import print

from tui_executor.client import MyClient
from tui_executor.utils import decode_traceback

LOGGER = logging.getLogger("tui-executor.kernel")
DEBUG = False


class KernelError(Exception):
    pass


class KernelInfo:
    """
    Information about the kernel process.

    Only one of the arguments is required, if the PID is given, the connection
    file will be determined from the process command line, if the connection
    file is given, the PID will be determined matching the key field in the
    connection file.

    Args:
        pid (int): the process identifier
        connection_file (str): the absolute path to the connection file
    """
    def __init__(self, pid: int = None, connection_file: str = None, kernel: MyKernel = None):
        self._pid = pid
        self._connection_file: str = connection_file
        self._kernel: MyKernel | None = kernel

        # Try to determine the PID if it is not given

        if not pid and connection_file:

            key = get_key(connection_file)

            # Search for the process that matches the above key

            for proc in find_kernel_processes():
                info = get_connection_info(proc)
                if info['key'] == key:
                    self._pid = proc.pid
                    break

        self._proc = psutil.Process(self._pid)
        self._cmdline = self._proc.cmdline()

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def creation_datetime(self):
        return datetime.datetime.fromtimestamp(self._proc.create_time())

    @property
    def kernel(self) -> MyKernel:
        return self._kernel

    @property
    def connection_file(self) -> str | None:
        if not self._connection_file:
            self._connection_file = get_connection_file(self._proc)

        return self._connection_file

    def __repr__(self):
        return f"KernelInfo(pid={self.pid})"


def find_kernel_processes() -> Iterator[psutil.Process]:
    """
    Search for processes that are Jupyter kernel processes.

    Kernel processes are identified when they have 'ipykernel' in their
    commandline. This might need to be refined in the future.

    Returns:
        A generator yielding Jupyter kernel process objects.
    """
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            for item in proc.cmdline():
                if "ipykernel" in item:
                    yield proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


def get_connection_file(proc: psutil.Process) -> str | None:
    """
    Returns the filename of the connection file that is associated with the
    kernel process. We assume indeed that the process that is given is a kernel
    process. Connections files are either matching 'kernel-<pid>.json' or a
    temporary file with the extension '.json'.

    Returns:
        The filename of the connection file or None when no match is found
        or when the file doesn't exist.
    """
    for item in proc.cmdline():

        # This is the default naming for the connection file

        match = re.search(r'kernel-(.*)\.json', item)
        if match:
            if Path(item).exists():
                return item
            else:
                warnings.warn(f"{item} doesn't exist.")
                return None

        # Not all connection files follow the above naming convention

        if item.endswith(".json"):
            # The additional check if the JSON file is a connection file is done because
            # not all connection files match 'kernel-(.*)\.json'.
            if Path(item).exists():
                with open(item) as fd:
                    connection_info = json.load(fd)
                    if "shell_port" not in connection_info:
                        warnings.warn(
                            f"The file {item} might not be a kernel connection file (it doesn't contain 'shell_port')."
                        )
                return item
            else:
                warnings.warn(f"{item} doesn't exist.")
                return None

    return None


def get_connection_info(proc: psutil.Process) -> dict:
    """
    Returns the connection info for the kernel process.

    A connection file is identified when its extension is '.json' and the file
    is a dictionary that contains the key 'shell_port'.

    Returns:
        A dictionary with the connection info or an empty dictionary.
    """
    for item in proc.cmdline():
        if item.endswith(".json"):
            # The additional check if the JSON file is a connection file is done because
            # not all connection files match 'kernel-(.*)\.json'.
            if Path(item).exists():
                with open(item) as fd:
                    connection_info = json.load(fd)
                    if "shell_port" not in connection_info:
                        warnings.warn(
                            f"The file {item} might not be a kernel connection file (it doesn't contain 'shell_port')."
                        )
                    return connection_info

    return {}


def get_key(connection_file: str | None) -> str | None:
    """
    Returns the value of the 'key' field in the connection file or None when
    there is no such key.
    """
    if not connection_file:
        return None

    with open(connection_file) as fd:
        connection_info = json.load(fd)
        return connection_info.get('key', None)


def find_running_kernels() -> Iterator[MyKernel]:
    """
    Returns a generator yielding kernel objects of type MyKernel. The kernel
    objects are created from the process ids of the running kernels and are
    marked not-to-own the kernel. The kernels can therefore not be killed by
    using the `shutdown()` method, use the original kernel object or kill
    them from the terminal.
    """
    kernel_processes = find_kernel_processes()

    for kernel_process in kernel_processes:
        try:
            yield MyKernel(kernel_process.pid)
        except FileNotFoundError:  # This happens when the connection_file doesn't exist
            continue

# Developer Info:
#
#      For the client class, a new client could be created as follows.
#
#        from jupyter_client import BlockingKernelClient
#
#        client = BlockingKernelClient()
#        client.load_connection_file('/Users/ebanner/Library/Jupyter/runtime/kernel-10962.json')
#        client.start_channels()
#
#    * see also
#      https://ipython.readthedocs.io/en/stable/development/wrapperkernels.html
#      https://github.com/ipython/ipykernel


class MyKernel:
    """
    Represents a Jupyter ipykernel. By default, if no arguments are provided,
    a ipykernel named 'python3' will be started. If you need another kernel,
    use the 'name' parameter with the name of the required terminal.

    You can find out which kernels are available on your system with the
    command:

        $ jupyter kernelspec list

    or programmatically, with the function: `MyKernel.get_kernel_spec()`.

    """
    def __init__(self, pid: int = None, name: str = "python3", startup_timeout: int = 60):
        if pid:
            self._kernel_info = KernelInfo(pid=pid)
            self._kernel_manager = KernelManager(owns_kernel=False)
            self._kernel_manager.load_connection_file(self._kernel_info.connection_file)
            self._kernel_manager.connection_file = self._kernel_info.connection_file
        else:
            self._kernel_manager = KernelManager(kernel_name=name)
            self._kernel_manager.start_kernel()
            self._kernel_info = KernelInfo(connection_file=self._kernel_manager.connection_file)

        self._startup_timeout = startup_timeout
        self._client = None
        self._error = None

    def get_pid(self) -> int:
        return self._kernel_info.pid

    def get_display_name(self):
        # with open(self.get_connection_file(), 'r') as fd:
        #     data: dict = json.load(fd)
        #     return data.get("display_name", "no display name")
        return self._kernel_manager.kernel_spec.display_name

    def is_alive(self) -> bool:
        return self._kernel_manager.is_alive()

    def get_kernel_type(self):
        return type(self._kernel_manager)

    def get_kernel_info(self) -> KernelInfo:
        return self._kernel_info

    def shutdown(self):
        self._kernel_manager.shutdown_kernel(now=True)

    def interrupt_kernel(self):
        self._kernel_manager.interrupt_kernel()

    def get_client(self) -> MyClient:
        if not self._client:
            self._client = MyClient(self)
        return self._client

    def get_kernel_manager(self):
        return self._kernel_manager

    @staticmethod
    def get_kernel_specs() -> Dict[str, str]:
        return jupyter_client.kernelspec.find_kernel_specs()

    def get_connection_file(self) -> str:
        return self._kernel_manager.connection_file

    def get_connection_info(self) -> Dict[str, int | str | bytes]:
        info = self._kernel_manager.get_connection_info(session=True)
        info.update(
            dict(
                connection_file=self._kernel_manager.connection_file,
                parent=self._kernel_manager,
            )
        )
        return info

    @staticmethod
    def _decode_io_msg_content(content: dict) -> str:

        if 'data' in content:  # Indicates completed operation
            return content['data']['text/plain']
        elif 'name' in content and content['name'] == "stdout":  # indicates output
            return content['text']
        elif 'traceback' in content:  # Indicates an error
            return decode_traceback(content['traceback'])
        else:
            return ''


def start_kernel(name: str, notify: Callable = lambda x: ..., cmd_log: str = None):

    kernel = MyKernel(name=name)
    notify(f"New kernel '{name}' started...")

    with MyClient(kernel) as client:

        info = client.get_kernel_info()
        if 'banner' in info:
            notify(info['banner'])

        # make sure the user doesn't by accident quit the kernel
        client.run_snippet("del quit, exit")

        # but allow the user to get out without quiting the kernel
        client.run_snippet(
            textwrap.dedent(
                """\
                def quit(keep_kernel=True): 
                    import IPython as ip
                    ip = ip.get_ipython()
                    ip.keepkernel_on_exit = keep_kernel
                    ip.ask_exit()
                """
            ))

        # If there is a startup script, run it now
        try:
            startup = os.environ["PYTHONSTARTUP"]
            notify(f"Loading Python startup file from {startup}.")
            client.run_snippet(
                textwrap.dedent(
                    """\
                    import os
                    import runpy

                    try:
                        startup = os.environ["PYTHONSTARTUP"]
                        runpy.run_path(path_name=startup)
                    except KeyError:
                        raise Warning("Couldn't load startup script, PYTHONSTARTUP not defined.")
                    except Exception as exc:
                        print(f"ERROR: loading startup script: {exc=}")
                    """
                    )
            )
        except KeyError:
            notify("Couldn't load startup script, PYTHONSTARTUP not defined.")

        if cmd_log:
            notify(
                f"Loading [blue]gui_executor.transforms[/] extension...log file in '{cmd_log}'"
            )
            client.run_snippet(
                textwrap.dedent(
                    f"""\
                    from gui_executor import transforms
                    transforms.set_log_file_location("{cmd_log}")
                    %load_ext gui_executor.transforms
                    """
                )
            )

    return kernel


def start_qtconsole(kernel: MyKernel,
                    buffer_size: int = 5000,
                    console_height: int = 42, console_width: int = 128,
                    console_font: str = "Courier New",
                    verbosity: int = 0):
    connection_file = kernel.get_connection_file()
    cmd_line = [
        f"jupyter",
        f"qtconsole",
        f"--ConsoleWidget.buffer_size={buffer_size} ",
        f"--ConsoleWidget.console_height={console_height} ",
        f"--ConsoleWidget.console_width={console_width} ",
        f"--ConsoleWidget.font_family='{console_font}' ",
        f"--existing {connection_file} --log-level=INFO",
    ]

    if find_spec('qtconsole') is None:
        raise ChildProcessError("The module qtconsole is not installed, command 'jupyter qtconsole' failed.")

    if verbosity:
        print("Starting Jupyter Qt Console...")
        print(f"{cmd_line = }")

    try:
        cmd = ExternalCommand(
            *cmd_line, capture=True, capture_stderr=True, asynchronous=True, shell=False)
        cmd.start()
    except ExternalCommandFailed as exc:
        raise ChildProcessError(cmd.error_message) from exc

    return cmd
