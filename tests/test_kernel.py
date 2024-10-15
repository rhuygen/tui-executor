import pytest
import rich

from tui_executor.kernel import MyKernel


@pytest.fixture(scope="module")
def kernel():
    kernel = MyKernel()

    yield kernel

    kernel.shutdown()
    del kernel  # explicitly shutdown the kernel


def test_kernel_is_alive(kernel):
    assert kernel.is_alive()


def test_kernel_types(kernel):
    rich.print()
    rich.print(f"kernel type = {kernel.get_kernel_type()}")
    rich.print(f"kernel client type: {type(kernel.get_client())}")


def test_get_connection_file(kernel):
    rich.print()
    rich.print(f"Connection file: {kernel.get_connection_file()}")


def test_get_connection_info(kernel):
    rich.print()
    rich.print(f"Connection info: ")
    rich.print(kernel.get_connection_info())


def test_kernel_specs(kernel):

    import rich

    rich.print()

    specs = kernel.get_kernel_specs()
    rich.print(specs)
