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
    """
    Utility function for loading outputs of :func:`extract` stored as ``json`` files
    into ``dicts`` containing data (nominal and sigma) in :class:`pd.DataFrame` objects.
    """
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
    """
    Extract worker function.

    Extracts data from provided ``path``, assuming it is the specified ``filetype``. The
    data is either returned as a ``dict``, where the data tables are dumped by :mod:`pandas`
    using the appropriate ``orient`` keyword, or they are returned with the data tables
    intact as :class:`pd.DataFrames`.

    .. warning::

        This feature has been introduced in ``yadg-5.0a2`` and is unstable.

    Parameters
    ----------

    filetype:
        Specifies the filetype. Can be both ``yadg``-native as well as a MaRDA extractors
        :class:`FileType`. Automatically checks for matches using the ``marda:`` prefix.

    path:
        A :class:`pathlib.Path` object pointing to the file to be extracted.

    as_dict:
        A :class:`bool` flag (default is ``True``) for toggling ``dict``-like export of
        extracted data (which can be written using :mod:`json`) instead of returning
        :class:`pd.DataFrames`.

    orient:
        A :class:`str` argument with which the :class:`pd.DataFrames` will be exported
        into :class:`dicts`.

    Returns
    -------

    ret: dict
        A dictionary containing the ``yadg_metadata`` and extracted ``content``. Within
        the content, the ``metadata`` contain any metadata present in the file, the
        ``values`` and ``sigmas`` contain the nominal values and sigmas of the extracted
        data, and ``units`` contain the units of columns of dimensional quantities.

    """

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
                "filename": str(path),
                "filetype": ftype.filetype,
            },
            "content": {
                "metadata": metadata,
                "units": units,
            },
        }

        if as_dict:
            ret["yadg_metadata"]["with_orient"] = orient
            ret["content"]["values"] = nominal.to_dict(orient=orient)
            ret["content"]["sigmas"] = sigma.to_dict(orient=orient)
        else:
            ret["content"]["values"] = nominal
            ret["content"]["sigmas"] = sigma

        return ret


__all__ = ["extract", "load_json"]
