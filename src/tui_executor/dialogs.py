
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.widgets import Label
from textual.widgets import Markdown


class YesNoDialog(ModalScreen[bool]):
    """A modal dialog that asks a YES / NO question."""

    BINDINGS = [Binding("escape", "dismiss(False)", "", show=False)]

    def __init__(self, question: str, title: str = None):
        super().__init__()

        self._title = title or "Question"
        self._question = question

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title)
            yield Markdown(self._question)
            with Horizontal():
                yield Button("Yes", variant="primary", id="btn-dialog-yes")
                yield Button("No", id="btn-dialog-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """React to button press."""

        if event.button.id == "btn-dialog-yes":
            self.dismiss(True)
            # self.app.query_one("#console-log", ConsoleOutput).write_log_info("You pressed YES...")
        else:
            self.dismiss(False)
            # self.app.query_one("#console-log", ConsoleOutput).write_log_info("You pressed NO...")
