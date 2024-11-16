Run Python functions from an automatically generated terminal app. 

## Global keys

| Key                | Command                        |
|--------------------|--------------------------------|
| `F1`               | This help                      |
| `ctrl-c, ctrl-q`   | Quit the application           |
| `d`                | Toggle dark/light theme        |
| `tab`, `shift-tab` | Focus the next/previous widget |
| `ctrl-p`           | Summon the command palette     |
| `escape`           | Bail out of the help           |


## Brief description

The TUI Executor app allows you to execute Python functions in a user-friendly environment in the Terminal. Any function that is decorated as a _Task_ will be associated with a button that you can click to execute the function. All these functions/tasks that are defined in the same Python module will appear under a collapsible section that is named after the module name (or a given name that we call the display name). If modules are organised in (sub-)packages, they will appear under a TAB that is named after the package name or the given display name.

TBW

## Task Arguments

TBW

## Task Output

TBW

## Tooltips

Tooltip are small, informative pop-up boxes that appear when you hover over certain elements of the TUI. The tooltips have a maximum width of 78 characters (+ 2 for a margin), keep that in mind when you write your docstring because too long lines will be wrapped. If you didn't write a docstring, no tooltip will be shown. 

We have tooltips implemented for the following widgets:

- Collapsible module sections:

  This will show the module level docstring that you created at the top of the Python file.  

- Task buttons:

  This will show the function level docstring for the function that is associated with this task button.

Write your docstrings with these tooltips in mind and make them user-oriented, i.e. describe **what** the task will do, **not how** it is working. Also, explain all task parameters, what type they are and what the default values are (if any).

> NOTE:
> There might be more widgets that have tooltips and that we forgot to document here.
