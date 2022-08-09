import sys
from importlib import metadata as ilmd
import warnings


def get_yadg_metadata() -> dict:
    """
    Returns current **yadg** metadata.
    """
    metadata = {"version": ilmd.version("yadg"), "command": " ".join(sys.argv)}
    return metadata


def deprecated(arg, depin="4.2", depout="5.0") -> None:
    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(
        f"'{arg}' has been deprecated in "
        f"yadg-{depin} and will stop working in yadg-{depout}",
        category=DeprecationWarning,
        stacklevel=2,
    )
    warnings.simplefilter("default", DeprecationWarning)
