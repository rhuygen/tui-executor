from tui_executor.funcpars import Empty


def test_empty():

    assert Empty is Empty
    assert Empty == Empty
    assert Empty() is Empty()
    assert Empty() == Empty()

    # Any arguments are swallowed and discarded

    assert Empty(1, 2, 3) is Empty()
    assert Empty() is Empty(1, 2, 3)

    assert Empty(1, 2, 3) == Empty()
    assert Empty() == Empty(1, 2, 3)

    assert Empty != Empty()
    assert Empty() != Empty

    # Not sure if this is a good idea and what we want. Do we want a Singleton to allow subclassing?

    class MyEmpty(Empty):
        def __init__(self, name: str):
            self.name = name

    assert MyEmpty("first new empty") is MyEmpty("second new empty")
    assert MyEmpty("first new empty") == MyEmpty("second new empty")
