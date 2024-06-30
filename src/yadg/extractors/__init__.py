import importlib
import logging
import json
from datatree import DataTree
from yadg import dgutils
from dgbowl_schemas.yadg.dataschema import ExtractorFactory, FileType


logger = logging.getLogger(__name__)


def extract(
    filetype: str,
    path: str,
    timezone: str = None,
    encoding: str = None,
    locale: str = None,
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
        A :class:`pathlib.Path` object pointing to the file to be extracted.

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

    return extract_from_path(path, extractor)


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

    # Func should always return a datatree.DataTree
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


def jsonize_orig_meta(obj: DataTree):
    for k in obj:
        if isinstance(obj[k], DataTree):
            jsonize_orig_meta(obj[k])
    if "original_metadata" in obj.attrs:
        obj.attrs["original_metadata"] = json.dumps(obj.attrs["original_metadata"])
    if "fulldate" in obj.attrs:
        obj.attrs["fulldate"] = int(obj.attrs["fulldate"])


__all__ = ["extract"]
