import sys
from importlib.metadata import version

from . import extractors
from .extractors import extract
from .main import run_with_arguments

__all__ = ["extract", "extractors", "run_with_arguments"]
__version__ = version("yadg")

sys.path += sys.modules["yadg"].__path__
