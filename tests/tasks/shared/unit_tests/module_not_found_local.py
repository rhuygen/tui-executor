from tui_executor.exec import exec_ui


@exec_ui(immediate_run=True)
def a_function_with_failed_import():

    # The following statement will generate the exception ModuleNotFoundError when the task is executed.

    import non_existing_module

    print("This message should never be printed.")
