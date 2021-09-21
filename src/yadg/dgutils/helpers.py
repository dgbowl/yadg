import sys
from helpers.version import _VERSION

def _yadg_metadata():
    metadata = {
        "version": _VERSION,
        "command": "".join(sys.argv)
    }
    return metadata
