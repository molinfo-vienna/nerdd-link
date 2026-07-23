"""Register nerdd-link's input, output, and converter plugins."""


def register() -> None:
    """Import modules whose classes register NERDD extensions."""
    from . import converters as _converters  # noqa: F401
    from . import input as _input  # noqa: F401
    from . import output as _output  # noqa: F401
