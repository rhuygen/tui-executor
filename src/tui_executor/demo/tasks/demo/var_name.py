from tui_executor.exec import exec_task
from tui_executor.utypes import VariableName

UI_MODULE_DISPLAY_NAME = "Passing known variables"


@exec_task()
def input_variable_name(a_float: float, model: VariableName("model")) -> str:
    """
    The argument 'model' is a variable that shall exist in the Python console
    (kernel). If not, executing the function will generate an error.
    """

    return f"{a_float=}, {type(a_float)=}, {model=}, {type(model)=}"


@exec_task()
def process_model(name: str = "LDO -> CSL", model: VariableName("ldo_model") = None):

    print(f"Processing model: {name}")
    print(f"{model = }")

    # ... your code comess here

    result = "The result of your processing..."

    return result


@exec_task(immediate_run=True)
def process_model_arg_immediately(model: VariableName("ldo_model")):
    print(f"Running model immediately... {model=}")


@exec_task(immediate_run=True)
def process_model_arg_only_immediately(model: VariableName("ldo_model"), /):
    print(f"Running model immediately... {model=}")


@exec_task(immediate_run=True)
def process_model_kwarg_immediately(model: VariableName("ldo_model") = None):
    print(f"Running model immediately... {model=}")


@exec_task(immediate_run=True)
def process_model_kwarg_only_immediately(*, model: VariableName("ldo_model")):
    print(f"Running model immediately... {model=}")


@exec_task(display_name="Source", capture_response=("ra", "dec"))
def get_radec(source: str):

    ra = 37.413
    dec = 89.264

    return ra, dec


@exec_task(display_name="Coordinates")
def show_radec(
        ra: VariableName("ra") = None,
        dec: VariableName("dec") = -13.4,
):
    print(f"ra = {ra}\ndec = {dec}")


@exec_task(immediate_run=True, capture_response="model")
def set_model() -> dict:
    """Define the variable 'model' in the kernel. 'model' is defined as a dict."""
    return {'model': "model C"}


@exec_task(immediate_run=True, capture_response="ldo_model")
def set_ldo_model() -> str:
    """Define the variable 'ldo_model' in the kernel. 'ldo_model' is a string."""
    return "LDO model A"
