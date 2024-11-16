"""
A demo app to demonstrate the capabilities of the tui-executor and to let you play
with the tasks that it provides.

The demo can be run as:

    $ python3 -m tui_executor.demo

"""
import os
import sys
from pathlib import Path

from tui_executor.app import TuiExecutorApp

HERE = Path(__file__).parent.resolve()

# Make sure the path with the modules for the demo is known to the Python interpreter
# running the App, but also to the kernel that will be started. So, bot sys.path and
# PYTHONPATH need to be adapted.

sys.path.append(str(HERE / "demo"))

python_path = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = str(HERE / "demo") + (f":{python_path}" if python_path else "")

module_path_list = [
    "tasks.demo",
]

app = TuiExecutorApp(module_path_list)
app.run()
