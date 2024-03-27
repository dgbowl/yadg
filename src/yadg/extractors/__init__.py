import importlib
import logging
from dgbowl_schemas.yadg.dataschema import ExtractorFactory
from pathlib import Path
from datatree import DataTree
from xarray import Dataset
from typing import Union
from yadg import dgutils, core

logger = logging.getLogger(__name__)


def extract(filetype: str, path: Path) -> Union[Dataset, DataTree]:
    """
    The extract functionality of yadg is implemented here.

    Extracts data from provided ``path``, assuming it is the specified ``filetype``. The
    data is either returned as a :class:`DataTree` or a :class:`Dataset`. In either case
    the returned objects have a :func:`to_netcdf` as well as a :func:`to_dict` method,
    which can be used to write the object into a file.

    Parameters
    ----------

    filetype:
        Specifies the filetype. Has to be a filetype supported by the dataschema.

    path:
        A :class:`pathlib.Path` object pointing to the file to be extracted.

    Returns
    -------
    Union[Dataset, DataTree]
        The extracted data and metadata.

    """
    extractor = ExtractorFactory(extractor={"filetype": filetype}).extractor

    m = importlib.import_module(f"yadg.extractors.public.{extractor.filetype}")
    func = getattr(m, "extract")

    ret = func(fn=str(path), **vars(extractor))
    ret.attrs = {
        "provenance": "yadg extract",
        "date": dgutils.now(asstr=True),
        "datagram_version": core.datagram_version,
        "yadg_extract_filename": str(path),
        "yadg_extract_filetype": str(extractor),
    }

    return ret


__all__ = ["extract"]
