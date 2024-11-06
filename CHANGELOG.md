# CHANGELOG for the TUI Executor Project

## Version 0.1.7 — 06/11/2024 — The Sorting Release

This release fixes the sorting of the TAbs, collapsible module sections and the function buttons. The TABs are sorted first according to the `UI_TAB_ORDER`, second in alphabetical order.

- [0.1.7] TABS are sorted alphabetically (capitals first)

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
