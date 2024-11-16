from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Checkbox
from textual.widgets import Input
from textual.widgets import Label

from tui_executor.funcpars import Empty
from tui_executor.funcpars import Parameter
from tui_executor.utypes import Callback
from tui_executor.utypes import TypeObject
from tui_executor.utypes import UWidget


class ArgumentsInput(Widget):

    def __init__(self, parameter: Parameter):
        super().__init__()

        self.parameter = parameter
        self.input_field = None

    def compose(self) -> ComposeResult:

        with Horizontal():
            yield Label(self.parameter.name)
            self.input_field = self.create_input()
            yield self.input_field

    def get_value(self) -> Any:
        input_field = self.query_one(f"#input-{self.parameter.name}")

        if isinstance(input_field, Checkbox):
            return input_field.value
        elif isinstance(input_field, UWidget):
            return input_field.get_value()

        value = input_field.value

        if not value:
            value = input_field.placeholder

        if not value or value.strip() == "None":
            return None

        return self.cast_argument(value)

    def create_input(self):
        placeholder_text = "" if self.parameter.default == Empty else str(self.parameter.default)

        if self.parameter.annotation is bool:
            input_field = Checkbox(value=False if self.parameter.default == Empty else True, id=f"input-{self.parameter.name}")
        elif isinstance(self.parameter.annotation, (TypeObject, Callback)):
            input_field = self.parameter.annotation.get_widget(id=f"input-{self.parameter.name}")
        else:
            input_field = Input(placeholder=placeholder_text, id=f"input-{self.parameter.name}")

        return input_field

    def cast_argument(self, value: str):

        try:
            if self.parameter.annotation is str:
                return value
            elif self.parameter.annotation is bool:
                return value
            elif self.parameter.annotation is int:
                return int(value)
            elif self.parameter.annotation is float:
                return float(value)

        except (ValueError, TypeError, SyntaxError):
            pass

        return value
