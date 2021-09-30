import sys
from importlib import metadata as ilmd

def _yadg_metadata():
    metadata = {
        "version": ilmd.version('yadg'),
        "command": "".join(sys.argv)
    }
    return metadata
