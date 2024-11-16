import contextlib
import logging
import queue
import textwrap
import threading
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple

from rich.console import Console
from rich.markup import escape
from rich.text import Text

from tui_executor.client import MyClient
from tui_executor.kernel import MyKernel
from tui_executor.utils import capture
from tui_executor.utils import create_code_snippet
from tui_executor.utils import stringify_args
from tui_executor.utils import stringify_kwargs

LOGGER = logging.getLogger("tui-executor.runnables")

DEBUG = False
"""Enable/disable all debugging log messages in this module."""


class FunctionRunnable(threading.Thread):

    def __init__(
            self,
            func: Callable, args: List, kwargs: Dict,
            input_queue: queue.Queue,
            notify: Callable = lambda x, y: ...
    ):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._response = None
        self._check_for_input = False
        self._input_patterns = []
        self._input_queue: queue.Queue = input_queue
        self._notify = notify

        self._running = False

    def check_for_input(self, patterns: Tuple):
        if patterns is not None:
            self._check_for_input = True
            self._input_patterns = [pattern.rstrip() for pattern in patterns]

    def run_in_current_interpreter(self):
        # This runs the function within the current Python interpreter. This might be a security risk
        # if you allow to run functions that are not under your control.

        self._running = True

        # self._notify('-' * 80, level=logging.INFO)

        DEBUG and self._notify(
            f"Running function {self._func.__name__}("
            f"{stringify_args(self._args)}{', ' if self._args else ''}{stringify_kwargs(self._kwargs)})...",
            level=logging.DEBUG
        )

        try:
            with capture() as out:
                self._response = self._func(*self._args, **self._kwargs)
            if out.stdout:
                self._notify(out.stdout, level=logging.NOTSET)
            if out.stderr:
                self._notify(out.stderr, level=logging.ERROR)
            if self._response is not None:
                self._notify(self._response, level=logging.NOTSET)
            success = True
        except Exception as exc:
            if out.stdout:
                self._notify(out.stdout, level=logging.NOTSET)
            if out.stderr:
                self._notify(out.stderr, level=logging.ERROR)
            self._notify(exc, level=logging.ERROR)
            success = False
        finally:
            # self._notify('-' * 80, level=logging.INFO)
            pass

        self._running = False

    def response(self):
        return self._response

    def handle_input_request(self, message: str = None) -> str:
        self._notify(message, level=logging.INFO)

        response = self._input_queue.get()
        self._input_queue.task_done()

        return response

    def is_running(self):
        return self._running

    @property
    def func_name(self):
        return self._func.__name__


class FunctionRunnableCurrentInterpreter(FunctionRunnable):
    def run(self):
        self.run_in_current_interpreter()


class FunctionRunnableKernel(FunctionRunnable):
    def __init__(
            self,
            kernel: MyKernel,
            func: Callable, args: List, kwargs: Dict,
            input_queue: queue.Queue,
            notify: Callable = lambda x, y: ...
    ):
        super().__init__(func, args, kwargs, input_queue, notify)
        self.kernel: MyKernel = kernel
        self.startup_timeout = 60  # seconds
        self.console = Console(record=True, width=240)

    def run(self):
        self.run_in_kernel()

    def run_in_kernel(self):
        self._running = True

        DEBUG and self._notify(f"----- Running script '{self.func_name}' in kernel", level=logging.DEBUG)

        snippet = create_code_snippet(self._func, self._args, self._kwargs)

        client = MyClient(self.kernel, startup_timeout=self.startup_timeout)
        try:
            client.connect()
        except RuntimeError as exc:
            self._notify(f"{exc}", level=logging.ERROR)
            return

        msg_id = client.execute(snippet, allow_stdin=True)

        DEBUG and self._notify(f"{id(client)}: {msg_id = }", level=logging.DEBUG)

        while True:
            try:
                io_msg = client.get_iopub_msg(timeout=1.0)

                if io_msg['parent_header']['msg_id'] != msg_id:
                    DEBUG and self._notify(f"{id(client)}: Skipping {io_msg = }", level=logging.DEBUG)
                    continue

                io_msg_type = io_msg['msg_type']
                io_msg_content = io_msg['content']

                DEBUG and self._notify(f"{id(client)}: {io_msg = }", level=logging.DEBUG)
                DEBUG and self._notify(f"{id(client)}: {io_msg_content = }", level=logging.DEBUG)

                if io_msg_type == 'stream':
                    if 'text' in io_msg_content:
                        text = io_msg_content['text'].rstrip()
                        self._notify(Text.from_ansi(text), level=logging.NOTSET)
                elif io_msg_type == 'status':
                    if io_msg_content['execution_state'] == 'idle':
                        # self.signals.data.emit("Execution State is Idle, terminating...")
                        DEBUG and self._notify(f"{id(client)}: Execution State is Idle, terminating...", level=logging.DEBUG)
                        # self.collect_response_payload(client, msg_id, timeout=1.0)
                        break
                    elif io_msg_content['execution_state'] == 'busy':
                        # self.signals.data.emit("Execution State is busy...")
                        DEBUG and self._notify(f"{id(client)}: Execution State is busy...", level=logging.DEBUG)
                        continue
                    elif io_msg_content['execution_state'] == 'starting':
                        # self.signals.data.emit("Execution State is starting...")
                        DEBUG and self._notify(f"{id(client)}: Execution State is starting...", level=logging.DEBUG)
                        continue
                elif io_msg_type == 'display_data':
                    if 'data' in io_msg_content:
                        DEBUG and self._notify(f"{id(client)}: display data of type {io_msg_content['data'].keys()}", level=logging.DEBUG)
                        if 'text/plain' in io_msg_content['data']:
                            text = io_msg_content['data']['text/plain'].rstrip()
                            self._notify(Text.from_ansi(text), level=logging.NOTSET)
                        elif 'text/html' in io_msg_content['data']:
                            text = io_msg_content['data']['text/html'].rstrip()
                            # self._notify(text, level=logging.NOTSET)
                        elif 'image/png' in io_msg_content['data']:
                            data = io_msg_content['data']['image/png']
                            # self.signals.png.emit(data)
                elif io_msg_type == 'execute_input':
                    ...  # ignore this message type
                    #     self.signals.data.emit("The code snippet:")
                    #     source_code = io_msg_content['code']
                    #     syntax = Syntax(source_code, "python", theme='default')
                    #     self.signals.data.emit(syntax)
                elif io_msg_type == 'error':
                    if 'traceback' in io_msg_content:
                        traceback = io_msg_content['traceback']
                        self._notify(Text.from_ansi('\n'.join(traceback)), level=logging.NOTSET)
                else:
                    self._notify(RuntimeError(f"Unknown io_msg_type: {io_msg_type}"), level=logging.ERROR)

            except queue.Empty:
                DEBUG and self._notify(f"{id(client)}: Catching on empty queue -----------", level=logging.DEBUG)
                # We fall through here when no output is received from the kernel. This can mean that the kernel
                # is waiting for input and therefore this is a good opportunity to check for stdin messages.
                with contextlib.suppress(queue.Empty):
                    in_msg = client.get_stdin_msg(timeout=0.1)

                    DEBUG and self._notify(f"{id(client)}: {in_msg = }", level=logging.DEBUG)

                    if in_msg['msg_type'] == 'input_request':
                        prompt = in_msg['content']['prompt']
                        response = self.handle_input_request(prompt)
                        client.input(response)
            except Exception as exc:
                # We come here after a kernel interrupt that leads to incomplete
                LOGGER.error(f"{id(client)}: Caught Exception: {exc}", exc_info=True)
                self._notify(exc, level=logging.ERROR)

        client.disconnect()

        self._running = False

    def handle_input_request(self, prompt: str = None) -> str:
        """
        This function is called when a stdin message is received from the kernel.

        Args:
            prompt: the text that was given as a prompt to the user

        Returns:
            A string that will be sent to the kernel as a reply.
        """
        if prompt:
            if self._check_for_input and all(pattern not in prompt for pattern in self._input_patterns):
                self._notify(
                    textwrap.dedent(
                        f"""\
                        [red][bold]ERROR: [/]The input request prompt message doesn't match any of the expected prompt messages.[/]
                        [default]→ input prompt='{escape(prompt)}'[/]
                        [default]→ expected=({", ".join(f"'{escape(x)}'" for x in self._input_patterns)})[/]

                        [blue]Ask the developer of the task to match up the input request patterns and the prompt.[/]
                        """
                    ),
                    level=logging.DEBUG
                )

            self._notify(escape(prompt), level=logging.DEBUG)
            self._notify(prompt, level=logging.DEBUG)

            response = self._input_queue.get()
            self._input_queue.task_done()
            return response
        else:
            # The input() function had no prompt argument
            self._notify(
                textwrap.dedent(
                    f"""\
                    [red][bold]ERROR: [/]No prompt was given to the input request function.[/]
                    An input request was detected from the Jupyter kernel, but no message was given to describe the 
                    request. Ask the developer of the task to pass a proper message to the input request.

                    [blue]An empty string will be returned to the kernel.[/]
                    """
                ),
                level=logging.DEBUG
            )
            return ''

    def collect_response_payload(self, client, msg_id, timeout: float):
        try:
            shell_msg = client.get_shell_msg(timeout=timeout)
        except queue.Empty:
            DEBUG and self._notify(f"{id(client)}: No shell message available for {timeout}s....", level=logging.DEBUG)
            self._notify(
                "[red]No result received from kernel, this might happen when kernel is interrupted.[/]",
                level=logging.ERROR
            )
            return

        msg_type = shell_msg["msg_type"]
        msg_content = shell_msg["content"]

        DEBUG and self._notify(f"{id(client)}: {shell_msg = }", level=logging.DEBUG)

        if msg_type == "execute_reply":
            status = msg_content['status']
            if status == 'error' and 'traceback' in msg_content:
                # We are not sending this traceback anymore to the Console output
                # as it was already handled in the context of the io_pub_msg.
                self._notify(f"{status = }", level=logging.ERROR)
                traceback = msg_content['traceback']
                self._notify(Text.from_ansi('\n'.join(traceback)), level=logging.ERROR)
