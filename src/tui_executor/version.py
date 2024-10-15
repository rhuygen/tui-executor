__all__ = [
    "__version__",
    "get_version",
]


def get_version():

    from importlib.metadata import version, PackageNotFoundError

    try:
        version = version("tui_executor")
    except PackageNotFoundError as exc:
        version = None

    return version


__version__ = get_version()
