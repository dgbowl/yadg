import sys
from .main import run_with_arguments

sys.path += sys.modules["yadg"].__path__

from . import _version

__version__ = _version.get_versions()["version"]
