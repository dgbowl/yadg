import importlib
import logging
from dgbowl_schemas.yadg import ExtractorFactory
from pydantic import ValidationError
from pathlib import Path
import pandas as pd
import json
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


def load_json(path: Path) -> dict:
    with path.open("r") as inf:
        js = json.load(inf)
    orient = js["yadg_metadata"]["with_orient"]
    for table in {"values", "sigmas"}:
        js["content"][table] = pd.DataFrame.from_dict(
            js["content"][table], orient=orient
        )
    return js


def extract(
    filetype: str, path: Path, as_dict: bool = True, orient: str = "tight"
) -> dict:

    for k in {filetype, f"marda:{filetype}"}:
        try:
            ftype = ExtractorFactory(extractor={"filetype": k}).extractor
            break
        except ValidationError:
            pass
    else:
        raise RuntimeError(f"Filetype '{filetype}' could not be understood.")

    if ftype.filetype in extractors:
        metadata, nominal, sigma, units = extractors[ftype.filetype](path, ftype)
        ret = {
            "yadg_metadata": {
                "version": importmeta.version("yadg"),
                "with_orient": orient,
                "filename": str(path),
                "filetype": ftype.filetype,
            },
            "content": {
                "metadata": metadata,
                "units": units,
            },
        }

        if as_dict:
            ret["content"]["values"] = nominal.to_dict(orient=orient)
            ret["content"]["sigmas"] = sigma.to_dict(orient=orient)
        else:
            ret["content"]["values"] = nominal
            ret["content"]["sigmas"] = sigma

        return ret


__all__ = ["extract", "load_json"]
