import sys
from importlib import metadata


def get_yadg_metadata() -> dict:
    """
    Returns current **yadg** metadata.
    """
    md = {
        "yadg_version": metadata.version("yadg"),
        "yadg_command": " ".join(sys.argv),
    }
    return md
