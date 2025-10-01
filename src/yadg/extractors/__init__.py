import importlib
import logging
import json
from functools import wraps
from functools import singledispatch
from typing import Any
from pathlib import Path
from xarray import DataTree
from yadg import dgutils
from dgbowl_schemas.yadg.dataschema import ExtractorFactory, FileType


logger = logging.getLogger(__name__)


def deprecate_fn_path(func):
    def handle_deprecated(param, *args, **kwargs):
        logger.warning(
            f"The parameter '{param}' is deprecated and has been replaced by 'source'. ({DeprecationWarning.__name__})",
        )
        source = kwargs.get("source", kwargs.pop(param))
        args = (source,) + args
        return args, kwargs

    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get("source") is not None:
            args = (kwargs.pop("source"),) + args
        elif kwargs.get("fn") is not None:
            args, kwargs = handle_deprecated("fn", *args, **kwargs)
        elif kwargs.get("path") is not None:
            args, kwargs = handle_deprecated("path", *args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def extract(
    filetype: str,
    path: Path | str,
    timezone: str = None,
    encoding: str = None,
    locale: str = None,
    **kwargs: dict,
) -> DataTree:
    """
    Extract data and metadata from a path using the supplied filetype.

    A wrapper around the :func:`extract_from_path` worker function, which creates a
    default extractor object. Coerces any :class:`str`s provided as ``path`` to :class:`Path`.

    Parameters
    ----------

    filetype:
        Specifies the filetype. Has to be a filetype supported by the dataschema.

    path:
        A :class:`Path` object pointing to the file to be extracted.

    timezone:
        A :class:`str` containing the TZ identifier, e.g. "Europe/Berlin".

    encoding:
        A :class:`str` containing the encoding, e.g. "utf-8".

    locale:
        A :class:`str` containing the locale name, e.g. "de_CH".

    """
    extractor = ExtractorFactory(
        extractor={
            "filetype": filetype,
            "timezone": timezone,
            "encoding": encoding,
            "locale": locale,
        }
    ).extractor

    return extract_from_path(Path(path), extractor, **kwargs)


@deprecate_fn_path
def extract_from_path(
    source: Path,
    extractor: FileType,
    **kwargs: dict,
) -> DataTree:
    """
    Extracts data and metadata from the provided path using the supplied extractor.

    The individual extractor functionality of yadg is called from here. The data is
    always returned as a :class:`DataTree`. The ``original_metadata`` entries in
    the returned objects are flattened using json serialisation. The returned objects
    have a :func:`to_netcdf` as well as a :func:`to_dict` method, which can be used to
    write the returned object into a file.

    Parameters
    ----------

    source:
        A :obj:`Path` pointing to the extracted file.

    extractor:
        A :class:`FileType` object describing the extraction process.
    """

    m = importlib.import_module(f"yadg.extractors.{extractor.filetype}")
    func = getattr(m, "extract")

    # Func should always return a xarray.DataTree
    ret: DataTree = func(source=source, **vars(extractor), **kwargs)
    jsonize_orig_meta(ret)

    ret.attrs.update(
        {
            "yadg_provenance": "yadg extract",
            "yadg_extract_date": dgutils.now(asstr=True),
            "yadg_extract_filename": str(source),
            "yadg_extract_Extractor": extractor.model_dump_json(exclude_none=True),
        }
    )
    ret.attrs.update(dgutils.get_yadg_metadata())

    return ret


def extract_from_bytes(
    source: bytes,
    extractor: FileType,
    **kwargs: dict,
) -> DataTree:
    """
    Extracts data and metadata from the provided raw bytes using the supplied extractor.

    The individual extractor functionality of yadg is called from here. The data is
    always returned as a :class:`DataTree`. The ``original_metadata`` entries in
    the returned objects are flattened using json serialisation. The returned objects
    have a :func:`to_netcdf` as well as a :func:`to_dict` method, which can be used to
    write the returned object into a file.

    Parameters
    ----------

    source:
        A :obj:`bytes` object containing the raw data to be extracted.

    extractor:
        A :class:`FileType` object describing the extraction process.
    """

    m = importlib.import_module(f"yadg.extractors.{extractor.filetype}")
    func = getattr(m, "extract")

    # Func should always return a xarray.DataTree
    ret: DataTree = func(source=source, **vars(extractor))
    jsonize_orig_meta(ret)

    ret.attrs.update(
        {
            "yadg_provenance": "yadg extract",
            "yadg_extract_date": dgutils.now(asstr=True),
            "yadg_extract_Extractor": extractor.model_dump_json(exclude_none=True),
        }
    )
    ret.attrs.update(dgutils.get_yadg_metadata())

    return ret


def jsonize_orig_meta(obj: DataTree):
    for k in obj:
        if isinstance(obj[k], DataTree):
            jsonize_orig_meta(obj[k])
    if "original_metadata" in obj.attrs:
        obj.attrs["original_metadata"] = json.dumps(obj.attrs["original_metadata"])
    if "fulldate" in obj.attrs:
        obj.attrs["fulldate"] = int(obj.attrs["fulldate"])


__all__ = ["extract"]


def get_extract_dispatch():
    @deprecate_fn_path
    @singledispatch
    def extract(
        source: Any,
        *,
        timezone: str,
        **kwargs: dict,
    ) -> DataTree:
        raise RuntimeError(
            f"The selected extractor does not support the source type {type(source)!r} "
            "provided. Please check the available extractors or enter a valid file path."
        )

    return extract
