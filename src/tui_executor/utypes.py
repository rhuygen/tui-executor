"""
The user types are class objects that are used as type hints for arguments in a functions that is decorated with the
`exec_ui`/`exec_task` decorator. Use these types if you need more control over input values for arguments to your
functions.

User types can of course be provided as part of your own package.

The user types provided by this module are:

  * CallBack: used when allowed values and defaults needs to be determined at run time
  * FixedList: a simple fixed list of values
  * ListList: a list of lists with the outer list expandable
  * VariableName: a variable from the REPL which shall be passed into the task

"""
from __future__ import annotations

import itertools
from pathlib import Path
from typing import Callable
from typing import List
from typing import Union

from textual.widget import Widget

# The following needs to be adapted to the Textual equivalents

QLineEdit = "LineEdit"
QCheckBox = "CheckBox"
QComboBox = None
Checked = True

HERE = Path(__file__).parent.resolve()


class TypeObject:
    def __init__(self, name: str = None):
        self.name = name

    @property
    def __name__(self):
        return self.name or self.__class__.__name__

    def get_widget(self):
        raise NotImplementedError


class UWidget(Widget):
    def __init__(self):
        super().__init__()

    def get_value(self):
        raise NotImplementedError

    def _cast_arg(self, field: QLineEdit | QCheckBox, literal: str | Callable):

        if literal is bool:
            return field.checkState() == Checked

        if not (value := field.displayText() or field.placeholderText()):
            return None

        try:
            return literal(value)
        except (ValueError, TypeError) as exc:
            print(f"Exception caught: {exc}")
            return value


class Callback(TypeObject):
    """
    A user type that can be used as a type hint in the arguments list of an `exec_ui` function. Use a call back when
    allowed values and defaults need to be determined when the button is clicked to generate the arguments panel
    instead of at import time.

    Args:
         func: the function/object to call that determines the type and values of this argument
         default: the function/object to call that determines the default value(s)
         name: the string to be displayed in the arguments panel. This is usually the type of the argument.
    """
    def __init__(self, func: Callable, default: Callable = None, name: str = None):
        super().__init__(name=name)
        self.func = func
        self.default_func = default

    def get_widget(self):
        return CallbackWidget(self.func, self.default_func)


class CallbackWidget(UWidget):
    def __init__(self, func: Callable, default_func: Callable):
        super().__init__()

        # Check for implementation with gui-executor

        self.widget = None

    def get_value(self):
        if not isinstance(self.widget, QComboBox):
            return self.widget.displayText() or self.widget.placeholderText()

        if isinstance(self.func_rc, (list, tuple)):
            return self.func_rc[self.widget.currentIndex()]
        else:
            return self.func_rc[self.widget.currentText()]


class VariableName(TypeObject):
    def __init__(self, value: str, name: str = "var_name"):
        super().__init__(name)
        self.value = value

    def get_widget(self):
        return VariableNameWidget(self.value)

    def get_value(self):
        return var_name(self.value)


class var_name:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class VariableNameWidget(UWidget):
    def __init__(self, value: str = None):
        super().__init__()
        self.value = value


    def get_value(self):
        return var_name(self.value)


class FixedList(TypeObject):
    """
    A user type for a simple List of fixed size.

    Args:
        literals: the types for each of the values in the list
        defaults: defaults for each of the values in the list
        name: the string to be used in the arguments panel to display the type or a description
    """
    def __init__(self, literals: List[Union[str, Callable]], defaults: List = None, name: str = None):
        super().__init__(name=name or "List")
        self._literals = literals
        self._defaults = defaults or []

    def __repr__(self):
        return f"List({self._literals} = {self._defaults})"

    def __iter__(self):
        return iter(itertools.zip_longest(self._literals, self._defaults))

    def get_widget(self):
        return FixedListWidget(self)


class FixedListWidget(UWidget):
    def __init__(self, type_object: FixedList):
        super().__init__()

        self._type_object = type_object
        self.fields = []

    def get_value(self) -> List:
        return [
            self._cast_arg(f, t)
            for f, (t, d) in zip(self.fields, self._type_object)
        ]


class ListList(TypeObject):
    """
    A user type for a list of lists. The outer list is extendable, rows can be added with a '+' button and
    removed with a 'x' button. The inner list is fixed and will be constructed from the literals and defaults.

    Args:
        literals: the types for each of the values in the inner lists
        defaults: defaults for each of the values in the first inner list
        name: the string to be used in the arguments panel to display the type or a description
    """

    def __init__(self, literals: List[Union[str, Callable]], defaults: List = None, name: str = None):
        super().__init__(name=name or "list of lists")
        self._literals = literals
        self._defaults = defaults or []

    def __repr__(self):
        return f"ListList({self._literals} = {self._defaults})"

    def __iter__(self):
        return iter(itertools.zip_longest(self._literals, self._defaults))

    def get_widget(self):
        return ListListWidget(self)


class ListListWidget(UWidget):
    def __init__(self, type_object: ListList):
        super().__init__()

        self._type_object = type_object
        self._rows = []

    def get_value(self) -> List[List]:
        return [
            [
                self._cast_arg(f, t)
                for f, (t, d) in zip(field, self._type_object)
            ] for field in self._rows
        ]
