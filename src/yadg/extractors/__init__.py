import importlib
import logging
from dgbowl_schemas.yadg.dataschema import ExtractorFactory
from pydantic import ValidationError
from pydantic.v1 import ValidationError as ValidationError_v1
from pathlib import Path
from zoneinfo import ZoneInfo
import xarray as xr
import datatree
from typing import Union
from yadg import dgutils, core
from dgbowl_schemas.yadg.dataschema import FileTypes

logger = logging.getLogger(__name__)

extractors = {}

for ftclass in FileTypes:
    filetype = ftclass.schema()["properties"]["filetype"]["const"]
    for modname in [
        f"yadg.extractors.public.{filetype}",
    ]:
        try:
            m = importlib.import_module(modname)
            if hasattr(m, "extract"):
                func = getattr(m, "extract")
                extractors[filetype] = func
                if hasattr(m, "supports"):
                    for k in getattr(m, "supports"):
                        extractors[k] = func
        except ImportError:
            continue


def extract(filetype: str, path: Path) -> Union[xr.Dataset, datatree.DataTree]:
    """
    Worker function of the ``extract`` subcommand.

    Extracts data from provided ``path``, assuming it is the specified ``filetype``. The
    data is either returned as a :class:`datatree.DataTree` or a :class:`xarray.Dataset`,
    however in either case the returned objects have a :func:`ret.to_netcdf()` as well
    as a :func:`ret.to_dict()` method, which can be used to write the file.

    .. warning::

        This feature has been introduced in ``yadg-5.0a2`` and is unstable.

    Parameters
    ----------

    filetype:
        Specifies the filetype. Can be both ``yadg``-native as well as a MaRDA extractors
        :class:`FileType`. Automatically checks for matches using the ``marda:`` prefix.

    path:
        A :class:`pathlib.Path` object pointing to the file to be extracted.

    Returns
    -------
    Union[xr.Dataset, datatree.DataTree]
        The extracted data and metadata, which can be written to ``NetCDF`` format using
        :func:`ret.to_netcdf()`.

    """
    for k in {filetype, f"marda:{filetype}"}:
        try:
            ftype = ExtractorFactory(extractor={"filetype": k}).extractor
            break
        except (ValidationError, ValidationError_v1) as e:
            logging.debug(e)
            pass
    else:
        raise RuntimeError(f"Filetype '{filetype}' could not be understood.")

    if ftype.filetype in extractors:
        ret = extractors[ftype.filetype](
            fn=str(path),
            encoding=ftype.encoding,
            timezone=ZoneInfo(ftype.timezone),
            locale=ftype.locale,
        )
        ret.attrs = {
            "provenance": "yadg extract",
            "date": dgutils.now(asstr=True),
            "datagram_version": core.datagram_version,
            "yadg_extract_filename": str(path),
            "yadg_extract_filetype": str(ftype),
        }

        return ret


__all__ = ["extract"]
