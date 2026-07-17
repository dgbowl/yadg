import importlib
import json
import logging
import os
import tempfile
import zipfile
from dgbowl_schemas.yadg.dataschema import ExtractorFactory, FileType
from functools import wraps
from functools import singledispatch
from pathlib import Path
from typing import Any
from xarray import DataTree
from yadg import dgutils


logger = logging.getLogger(__name__)


def extract(
    filetype: str,
    path: Path | str,
    timezone: str = None,
    encoding: str = None,
    locale: str = None,
    suffix: str = None,
    **kwargs: dict,
) -> DataTree:
    """
    Extract data and metadata from a path using the supplied filetype.

    A wrapper around the :func:`extract_from_path` and :func:`extract_from_zip` worker functions.
    Creates a default extractor object for a given ``filetype``. Coerces any :class:`str`s provided
    as ``path`` to :class:`Path`. If the provided ``path`` is a zip file, it is treated as such.

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

    suffix:
        A :class:`str` containing a non-default suffix for matching files within a zip file.

    """
    extractor = ExtractorFactory(
        extractor={
            "filetype": filetype,
            "timezone": timezone,
            "encoding": encoding,
            "locale": locale,
        }
    ).extractor

    if suffix is not None:
        extractor.suffix = [suffix]
    path = Path(path)
    if path.suffix == ".zip" and zipfile.is_zipfile(path):
        logger.info("Processing zipfile")
        return extract_from_zip(path, extractor, **kwargs)
    else:
        return extract_from_path(path, extractor, **kwargs)


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
    ret: DataTree = func(source, **vars(extractor), **kwargs)
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


def extract_from_zip(
    source: Path,
    extractor: FileType,
    ignore_merge_errors: bool = False,
    **kwargs: dict,
) -> DataTree:
    """
    Extracts data and metadata from the provided zip file path using the supplied extractor.

    The zip file is extracted into a temporary directory, and all top-level files that match
    the :obj:`extractor.suffix`, are then processed. Metadata in the files within the zip file
    are combined strictly, unless :obj:`ignore_merge_errors` is set to :obj:`True`.


    Parameters
    ----------

    source:
        A :obj:`Path` pointing to the zip file.

    extractor:
        A :class:`FileType` object describing the extraction process.

    ignore_merge_errors:
        A :class:`bool` for enforcing metadata consistency.
    """

    m = importlib.import_module(f"yadg.extractors.{extractor.filetype}")
    func = getattr(m, "extract")

    zf = zipfile.ZipFile(source)
    strict_merge = not ignore_merge_errors
    if strict_merge is False:
        logger.info(
            "Will drop metadata conflicts in individual %s files.",
            extractor.filetype,
        )

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        dtdict = None
        filenames = []
        for ffn in os.listdir(tempdir):
            for suffix in extractor.suffix:
                if ffn.endswith(suffix):
                    filenames.append(ffn)
        if len(filenames) == 0:
            logger.critical(
                "No files of filetype '%s' were found in the zip file using suffix %s.",
                extractor.filetype,
                extractor.suffix,
            )

        for ffn in sorted(filenames):
            logger.debug("Processing filename '%s'", ffn)
            path = Path(tempdir) / ffn
            fdt = func(path, **vars(extractor))
            jsonize_orig_meta(fdt)
            dtdict = dgutils.merge_dicttrees(dtdict, fdt.to_dict(), strict_merge)

    ret = DataTree.from_dict(dtdict)
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
