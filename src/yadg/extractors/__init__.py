import importlib
import logging
import json
from xarray import DataTree
from yadg import dgutils
from dgbowl_schemas.yadg.dataschema import ExtractorFactory, FileType


logger = logging.getLogger(__name__)


def extract(
    filetype: str,
    path: str,      # TODO maybe rename this to something like source?
    timezone: str = None,
    encoding: str = None,
    locale: str = None,
    extract_func: str = "extract",
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

    path:
        A :class:`pathlib.Path` object pointing to the file to be extracted.    # TODO

    timezone:
        A :class:`str` containing the TZ identifier, e.g. "Europe/Berlin".

    encoding:
        A :class:`str` containing the encoding, e.g. "utf-8".

    locale:
        A :class:`str` containing the locale name, e.g. "de_CH".

    extract_func:
        A :class:`str` containing the extractor function to use, e.g. "extract_raw_content".
        The default "extract" is using the file path to extract data.

    """
    extractor = ExtractorFactory(
        extractor={
            "filetype": filetype,
            "timezone": timezone,
            "encoding": encoding,
            "locale": locale,
        }
    ).extractor

    return extract_from_source(path, extractor, extract_func)


# TODO this function can probably be removed
def extract_from_path(
    path: str,
    extractor: FileType,
) -> DataTree:
    """
    Extracts data and metadata from the provided path using the supplied extractor.

    The individual extractor functionality of yadg is called from here. The data is
    always returned as a :class:`DataTree`. The ``original_metadata`` entries in
    the returned objects are flattened using json serialisation. The returned objects
    have a :func:`to_netcdf` as well as a :func:`to_dict` method, which can be used to
    write the returned object into a file.
    """

    m = importlib.import_module(f"yadg.extractors.{extractor.filetype}")
    func = getattr(m, "extract")

    # Func should always return a xarray.DataTree
    ret: DataTree = func(fn=path, **vars(extractor))
    jsonize_orig_meta(ret)

    ret.attrs.update(
        {
            "yadg_provenance": "yadg extract",
            "yadg_extract_date": dgutils.now(asstr=True),
            "yadg_extract_filename": str(path),
            "yadg_extract_Extractor": extractor.model_dump_json(exclude_none=True),
        }
    )
    ret.attrs.update(dgutils.get_yadg_metadata())

    return ret


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
