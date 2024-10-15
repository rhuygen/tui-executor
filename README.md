
# TUI Executor

You ever wanted to execute your Python code from a simple TUI without the need to use a REPL or commandline? Look no further, use TUI Executor.


## Installation

Install this package in your virtual environment:

```
$ python3 -m pip install [--upgrade] tui-executor 
```

## Documentation

You can find the documentation at https://ivs-kuleuven.github.io/tui-executor/.


## Running the Tests

From the project folder, run the following command:

```
$ PYTHONPATH=tests tui-executor --module-path tasks.shared --module-path tasks.specific --debug
```
