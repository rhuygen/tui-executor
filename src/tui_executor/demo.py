"""
A demo app to demonstrate the capabilities of the tui-executor and to let you play
with the tasks that it provides.

The demo can be run as:

    $ python3 -m tui_executor.demo

"""
import sys
from pathlib import Path

from tui_executor.app import TuiExecutorApp

HERE = Path(__file__).parent.resolve()

sys.path.append(str(HERE / "../../demo"))

module_path_list = [
    "tasks.docs",
]

app = TuiExecutorApp(module_path_list)
app.run()
