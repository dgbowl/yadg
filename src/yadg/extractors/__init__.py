import importlib
import logging
from dgbowl_schemas.yadg import FileType
from pathlib import Path
from typing import Callable
from importlib import metadata as importmeta

logger = logging.getLogger(__name__)

extractors = {}

for modname in {"eclabmpr", "eclabmpt"}:
    try:
        m = importlib.import_module(f"yadg.extractors.{modname}")
        supp = getattr(m, "supports")
        func = getattr(m, "extract")
        for k in supp:
            extractors[k] = func
    except ImportError as e:
        logger.critical(f"could not import module '{modname}'")
        raise e


def as_dict(
    func: Callable,
    path: Path,
    filetype: FileType,
    orient: str = "tight",
) -> dict:
    
    metadata, nominal, sigma, units = func(path, filetype)

    ret = {
        "yadg_metadata": {
            "version": importmeta.version("yadg"),
            "with_orient": orient,
            "filename": str(path),
            "filetype": filetype.filetype,
        },
        "content": {
            "metadata": metadata,
            "values": nominal.to_dict(orient=orient),
            "sigmas": sigma.to_dict(orient=orient),
            "units": units
        }
    }

    return ret


def extract(filetype: FileType, path: Path):
    if filetype.filetype in extractors:
        f = extractors[filetype.filetype]
        return as_dict(func=f, path=path, filetype=filetype)


__all__ = ["extract"]
