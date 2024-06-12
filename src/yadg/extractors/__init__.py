import importlib
import logging
from pathlib import Path
from datatree import DataTree
from yadg import dgutils, core
from dgbowl_schemas.yadg.dataschema import ExtractorFactory


logger = logging.getLogger(__name__)


def extract(
    filetype: str,
    path: Path,
    timezone: str = None,
    encoding: str = None,
    locale: str = None,
) -> DataTree:
    """
    The individual extractor functionality of yadg is called from here.

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

    """
    extractor = ExtractorFactory(
        extractor={
            "filetype": filetype,
            "timezone": timezone,
            "encoding": encoding,
            "locale": locale,
        }
    ).extractor

    m = importlib.import_module(f"yadg.extractors.{extractor.filetype}")
    func = getattr(m, "extract")

    # Func should always return a datatree.DataTree
    ret = func(fn=str(path), **vars(extractor))
    ret.attrs = {
        "yadg_provenance": "yadg extract",
        "yadg_extract_date": dgutils.now(asstr=True),
        "yadg_datagram_version": core.datagram_version,
        "yadg_extract_filename": str(path),
        "yadg_extract_filetype": str(extractor),
    }

    return ret


__all__ = ["extract"]
