from tui_executor.exec import exec_task


@exec_task(immediate_run=True)
def print_this():
    import this
