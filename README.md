
# TUI Executor

You ever wanted to execute your Python code from a simple TUI without the need to use a REPL or commandline? Look no further, use TUI Executor.


## Installation

Install this package in your virtual environment:

```
$ python3 -m pip install [--upgrade] tui-executor 
```

## Documentation

You can find the documentation at https://rhuygen.github.io/tui-executor/.


## Running the Demo

You can run a demo of the app with the following command:

```shell
$ python3 -m tui_executor.demo
```

This will start the app with a number of tasks that demonstrate the capabilities of the `tui-executor` app.

## Running the app with test tasks

This assumes you have cloned the git repository and navigated to the project folder. There you should do a `pip install -e .` to have a working editable installation.

From the project folder, run the following command to test the app's capabilities:

```shell
$ PYTHONPATH=tests tui-executor --module-path tasks.docs
```

You can add more module paths as argument to the above command. This will create additional TABs for each (sub-)package in that module path.

```shell
$ PYTHONPATH=tests tui-executor --module-path tasks.docs --module-path tasks.specific --module-path tasks.shared
```
