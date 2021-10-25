import sys
from importlib import metadata as ilmd


def get_yadg_metadata() -> dict:
    """
    Returns current **yadg** metadata.
    """
    metadata = {"version": ilmd.version("yadg"), "command": " ".join(sys.argv)}
    return metadata
