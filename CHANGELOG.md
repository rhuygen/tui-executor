# CHANGELOG for the TUI Executor Project

## Version 0.4.0 — 16/11/2024 — The Running in the Kernel Release

This release focussed on running the tasks in the IPython kernel, which is started automatically during initialisation of the app. The release also allows you to choose another already running kernel. Code snippets will then be executed in that kernel. 

Its a big release with lots of fixes and additions.

- [0.4.0] Some unit tests have been updated or fixed.
- [0.4.0] User types are now working as expected.
- [0.4.0] The output of snippet code is slightly improved.
- [0.4.0] The Arguments panel is now fully functional.
- [0.4.0] Use CTRL+q to quit the app, instead of just 'q'.
- [0.4.0] Function names will be displayed in the task button with maximum 32 characters (defined by the MAX_WIDTH_FUNCTION_NAME). Use `display_name` if you want to have a nicer label in the task button.
- [0.4.0] You can choose to connect to an existing kernel
- [0.4.0] A new dialog 'SelectDialog' is added. You can choose an option out of a list of choices.
- [0.4.0] Tasks are now running in the kernel and output is sent to the ConsoleOutput panel
- [0.4.0] The demo module is now called `tasks.demo`.
- [0.3.3] Small improvements to ConsoleOutput widget
- [0.3.3] Fixed the tui_executor.demo script to configure the PYTHONPATH correctly for the kernel
- [0.3.3] Added DEFAULT_CONSOLE_OUTPUT_WIDTH to be used for Console and Panel width
- [0.3.3] Improved some demo tasks and added a unit test task to test the output of a task in the console while the task is still running.


## Version 0.3.2 — 12/11/2024 — The Small Improvements Release

- [0.3.2] improve message logging to the console output, adding the level
- [0.3.2] improve some docstrings
- [0.3.1] fixed the location of the demo tasks

## Version 0.3.0 — 11/11/2024 — The Kernels Release

This release adds kernel and client support as a prototype, but it needs some more work to become stable and needs functionality to select an existing kernel and use that kernel when running tasks.

- [0.3.0] 🚧 done major refactoring of the kernel and client modules.
- [0.3.0] added a Yes / No modal dialog
- [0.3.0] replaced RichLog with a new subclass ConsoleOutput
- [0.3.0] Small update to run_function which now sends messages to the ConsoleOutput instead of to the Textual log.

## Version 0.2.0 — 08/11/2024 — The Arguments Release

Let's go to version 0.2.x now that we move to the implementation of the arguments panel. This is the next step to bring us closer to a fully working TUI Executor.

- [0.2.0] it takes longer before the tooltip appears when hovering a button
- [0.2.0] buttons are styled better with hover and focus
- [0.2.0] 🚧 started with run_task for immediate_run functions
- [0.2.0] added tasks to demo for immediate_run demonstration
- [0.2.0] small maintenance changes in several functions

## Version 0.1.12 — 07/11/2024 — The Information is Knowledge Release

This release implements tooltips for the collapsible module sections and for the task buttons. If a docstring exists at module level or at function level, it will be shown in a tooltip when the user hovers over the widget.

I also change the build system from setuptools to hatchling.

- [0.1.12] Changed build system to hatchling
- [0.1.12] small updates to `README.md`
- [0.1.12] added a demo and demo tasks to the project
- [0.1.11] added a `tooltips.py` module to demonstrate the tooltips in the demo
- [0.1.11] Tooltips implemented for task buttons
- [0.1.11] Tooltips implemented for collapsible module sections
- [0.1.11] small updates of the `help.md` 

## Version 0.1.10 — 06/11/2024 — The Sorting Release

This release fixes the sorting of the TABs, collapsible module sections and the function buttons. Empty TABs and panels are omitted.

- [0.1.10] function buttons are now sorted in the order they appear in the source module instead of alphabetically
- [0.1.9] allow Python >= 3.8
- [0.1.8] fix a problem in the build where the 'app.tcss' and 'help.md' were missing
- [0.1.7] the collapsible module panels are now also sorted alphabetically
- [0.1.7] collapsible module panels that are empty, i.e. do not contain task buttons, are omitted
- [0.1.7] TABS are sorted alphabetically (capitals first)
- [0.1.7] TABS that are empty, i.e. do not contain any modules, are omitted

## Version 0.1.6 — 06/11/2024 — The Navigation Release

This release fixes the TABs, the collapsible module sections and task buttons in the navigation panel at the left part of the TUI. The buttons and sections have the correct names and labels. The actions associated with button presses are not yet implemented.

- [0.1.6] Master Screen refactored to handle packages, modules and functions/tasks. The TABs, collapsible modules and function buttons are now properly rendered.
- [0.1.6] more consistent use of module_path and module_path_list
- [0.1.6] its now much clearer when dotted module path or directory path is returned
- [0.1.6] added ArgumentsPanel, ModulePanel, and PackagePanel
- [0.1.6] support for commandline argument `--module-path`
- [0.1.6] added many docstrings for modules and functions
- [0.1.6] further fixes to unit tests (WIP)
- [0.1.6] added Textual version info to the help screen

## Version 0.1.5 — 05/11/2024

- [0.1.5] renamed `args.py` to `funcpars.py`
- [0.5.1] added a `Singleton` base class and `Empty` is now a Singleton.
- [0.1.5] fixed a number of unit tests

## Version 0.1.4 — 04/11/2024

- [0.1.4] Updated docs to refer to TUI instead of GUI
- [0.1.4] Created a first working prototype to demonstrate the TUI layout and widgets 
- [0.1.4] Rearranged classes and modules

## Version 0.1.3 — 15/10/2024

- [0.1.3] Added this project to GitHub
- [0.1.3] Started to clean up the old code that we inherited from the `gui-executor` project.
- [0.1.3] Cleaned up kernel and client code + unit tests

## Version 0.1.2 — 14/10/2024

- [0.1.2] Small fixes in the pyproject.toml and the README file
- [0.1.1] Added this CHANGELOG
- [0.1.1] Project is in the Pre-Alpha state.
- [0.1.0] This is the initial version of the Project.
- [0.1.0] This project is based on the existing `gui-executor` project.
- [0.1.0] The project is ready to be uploaded to PyPI.
