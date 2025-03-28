import importlib
import logging
import json
from xarray import DataTree
from yadg import dgutils
from dgbowl_schemas.yadg.dataschema import ExtractorFactory, FileType


logger = logging.getLogger(__name__)


def extract(
    filetype: str,
    source: str | bytes = None,
    timezone: str = None,
    encoding: str = None,
    locale: str = None,
    extract_func: str = "extract",
    path: str = None,
    **kwargs: dict,
) -> DataTree:
    """
    Extract data and metadata from a path using the supplied filetype.

    A wrapper around the :func:`extract_from_path` worker function, which creates a
    default extractor object.

    Parameters
    ----------

    filetype:
        Specifies the filetype. Has to be a filetype supported by the dataschema.

    source:
        Raw bytes of the file to be extracted, e.g. a file path or raw bytes of an mpr file.

    timezone:
        A :class:`str` containing the TZ identifier, e.g. "Europe/Berlin".

    encoding:
        A :class:`str` containing the encoding, e.g. "utf-8".

    locale:
        A :class:`str` containing the locale name, e.g. "de_CH".

    extract_func:
        A :class:`str` containing the extractor function to use, e.g. "extract_raw_content".
        Options:
            - "extract" (default): Uses the file path to extract data.
            - "extract_raw_content": Directly extracts from raw contents like bytes of an mpr file.

    path:
        Deprecated. Can now be specified using the source parameter.
        A :class:`pathlib.Path` object pointing to the file to be extracted.
    """
    if path is not None:
        logger.info(
            "The parameter 'path' is deprecated and has been replaced by 'source'. "
            "Please use 'source' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        source = path

    if source is None:
        raise ValueError("A valid 'source' must be provided.")

    extractor = ExtractorFactory(
        extractor={
            "filetype": filetype,
            "timezone": timezone,
            "encoding": encoding,
            "locale": locale,
        }
    ).extractor

    return extract_from_source(path, extractor, extract_func)


def extract_from_source(
    source: str,
    extractor: FileType,
    extractor_func: str = "extract",
) -> DataTree:
    m = importlib.import_module(f"yadg.extractors.{extractor.filetype}")
    func = getattr(m, extractor_func)

    # Func should always return a xarray.DataTree
    if extractor_func == "extract":
        ret: DataTree = func(fn=source, **vars(extractor))      # TODO would be best to change all fn to source?
    else:
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
    if extractor_func == "extract":
        ret.attrs.update({"yadg_extract_filename": str(source),})

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
