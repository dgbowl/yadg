import importlib
import logging
from dgbowl_schemas.yadg import FileType
from pathlib import Path

logger = logging.getLogger(__name__)

extractors = {}

for modname in {
    "eclabmpr",
    "eclabmpt"
}:
    try:
        m = importlib.import_module(f"yadg.extractors.{modname}")
        supp = getattr(m, "supports")
        func = getattr(m, "extract")
        for k in supp:
            extractors[k] = func
    except ImportError as e:
        logger.critical(f"could not import module '{modname}'")
        raise e


def extract(filetype: FileType, path: Path):
    print(f"{filetype=}")
    print(f"{path=}")
    if filetype.filetype in extractors:
        print(f"{extractors[filetype.filetype]=}")
        f = extractors[filetype.filetype]
        return f(path=path, filetype=filetype)


__all__ = ["extract"]