import sys
from .main import run_with_arguments
from . import _version

__all__ = ["run_with_arguments"]
__version__ = _version.get_versions()["version"]

sys.path += sys.modules["yadg"].__path__
