
# The variable 'first_script' was defined in the first_script_with_kernel
# The purpose of this script is to test if we run in the same kernel.

if 'first_script' not in locals() and 'first_script' not in globals():
    raise NameError("The variable `first_script` is not found in locals(), nor globals().")

if first_script != 42:
    raise ValueError(f"Expected the value 42 for first_script, got {first_script=}")

print(first_script)
