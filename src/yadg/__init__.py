import sys

sys.path += sys.modules["yadg"].__path__
from .main import run_with_arguments
