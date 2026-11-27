import sys
from importlib.metadata import version

from . import extractors
from .main import run_with_arguments

__all__ = ["extractors", "run_with_arguments"]
__version__ = version("yadg")

sys.path += sys.modules["yadg"].__path__
