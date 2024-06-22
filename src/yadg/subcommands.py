import os
import logging
import json
import yaml
import shutil
import hashlib
from pathlib import Path
from datatree import DataTree
from xarray import Dataset

from dgbowl_schemas.yadg import to_dataschema
from yadg import core, dgutils, extractors


logger = logging.getLogger(__name__)


def _load_file(infile: str) -> dict:
    with open(infile, "r") as inf:
        if infile.endswith("json"):
            obj = json.load(inf)
        elif infile.endswith("yml") or infile.endswith("yaml"):
            obj = yaml.safe_load(inf)
        else:
            logging.critical("Filename type not recognised: '%s'", infile)
            raise RuntimeError(f"Filename type not recognised: '{infile}'")
    return obj


def _zip_file(folder: str, outpath: str, method: str = "zip") -> str:
    if method in {"zip", "tar"}:
        fn = f"{outpath}.{method}"
    elif method in {"bztar", "gztar", "xztar"}:
        fn = f"{outpath}.tar.{method[:2]}"
        if method == "bztar":
            fn = f"{fn}2"
    logger.debug("Archiving.")
    shutil.make_archive(outpath, method, root_dir=folder)
    logger.debug("Hashing.")
    m = hashlib.sha1()
    with open(fn, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            m.update(chunk)
    return fn, m.hexdigest()


def _obj_to_meta_dict(dt: DataTree) -> dict:
    ret = {}
    for k, v in dt.to_dict().items():
        if isinstance(v, Dataset):
            ret[k] = v.to_dict(data=False)
        elif isinstance(v, DataTree):
            ret[k] = _obj_to_meta_dict(v)
        else:
            raise RuntimeError(f"Object {k!r} is type {type(v)!r}.")
    return ret


def process(
    *,
    infile: str,
    outfile: str,
    ignore_merge_errors: bool,
    **kwargs: dict,
) -> None:
    """
    The ``process`` subcommand of yadg.

    This function first checks that the supplied ``infile`` exists, is a valid
    dataschema, and if yes, proceeds to process the dataschema into a datatree. If
    this is successful, the datatree is written out into ``outfile`` (which is
    ``"datagram.nc"`` by default).

    """
    assert os.path.exists(infile) and os.path.isfile(infile), (
        f"Supplied dataschema filename '{infile}' does not exist "
        "or is not a valid file."
    )

    logger.info(f"Reading input file from '{infile}'.")
    schema = _load_file(infile)

    logger.info("Loading dataschema.")
    inobj = to_dataschema(**schema)
    ds = dgutils.update_schema(inobj)

    logger.debug("Processing dataschema")
    datagram = core.process_schema(ds, strict_merge=not ignore_merge_errors)

    logger.info("Saving datatree to '%s'.", outfile)
    datagram.to_netcdf(outfile, engine="h5netcdf")


def update(
    *,
    infile: str,
    outfile: str,
    **kwargs: dict,
) -> None:
    """
    The ``update`` subcommand of yadg.

    This function updates the dataschema present in the ``infile`` to comply with the
    newest version of dataschema, and saves the resulting object into ``outfile`` (which
    is the ``infile`` with  a `".new.json"` suffix by default).

    """
    assert os.path.exists(infile) and os.path.isfile(infile), (
        f"Supplied dataschema filename '{infile}' does not exist "
        "or is not a valid file."
    )

    logger.info("Reading input file from '%s'.", infile)
    inobj = _load_file(infile)

    if outfile is None:
        name, ext = os.path.splitext(infile)
        outfile = f"{name}.new.json"

    outobj = dgutils.update_schema(inobj)

    logger.info("Writing new dataschema into '%s'.", outfile)
    with open(outfile, "w") as out:
        json.dump(outobj.model_dump(), out, indent=1)


def preset(
    *,
    preset: str,
    folder: str,
    outfile: str,
    process: bool,
    archive: bool,
    packwith: str,
    ignore_merge_errors: bool,
    **kwargs: dict,
) -> None:
    """
    The ``preset`` subcommand of yadg.

    If ``folder`` is an existing folder and ``preset`` a valid dataschema template file,
    this function will prepend the specified ``folder`` to all relative paths in the
    ``preset``, converting them to absolute paths.

    The resulting dataschema will be saved in the supplied ``outfile``.

    Alternatively, if ``process`` is specified, the created dataschema will be
    directly processed into a datatree, which is then saved in ``outfile``.

    Additionally, the contents of the ``folder`` can be archived (if ``archive`` is
    set), using a compression algorithm of your choice.

    """
    assert os.path.exists(folder) and os.path.isdir(folder), (
        f"Supplied folder path '{folder}' does not exist " "or is not a valid folder."
    )

    if not os.path.isabs(folder) and not process:
        logger.warning(
            f"The provided path '{folder}' is a relative path. The generated schema "
            "likely will not work outside current working directory."
        )

    assert os.path.exists(preset) and os.path.isfile(preset), (
        f"Supplied preset path '{preset}' does not exist " "or is not a valid file."
    )

    logger.info("Reading input file from '%s'.", preset)
    preset = _load_file(preset)

    logger.info("Processing preset as schema.")
    schema = to_dataschema(**preset)

    logger.info("Creating a schema from preset for '%s'.", folder)
    ds = dgutils.update_schema(dgutils.schema_from_preset(schema, folder))

    logger.info("Loaded dataschema version '%s'", ds.version)
    if process:
        logger.info("Processing created schema.")
        datagram = core.process_schema(ds, strict_merge=not ignore_merge_errors)
        outfile = "datagram.nc" if outfile is None else outfile
        if archive:
            zipfile = outfile.replace(".nc", "")
            logger.info("Zipping input folder into '%s'", zipfile)
            fn, hash = _zip_file(folder, zipfile, method=packwith)
            datagram.attrs["data_archive_sha-1"] = hash
            datagram.attrs["data_archive_path"] = fn
        logger.info("Saving datagram to '%s'.", outfile)
        datagram.to_netcdf(outfile, engine="h5netcdf")
    else:
        if archive:
            logger.warning(
                "The --archive option must be supplied along with --process. "
                "Continuing without archiving."
            )
        outfile = "schema.json" if outfile is None else outfile
        logger.info("Saving schema to '%s'.", outfile)
        with open(outfile, "w") as ofile:
            json.dump(ds.model_dump(), ofile, indent=1)


def extract(
    *,
    filetype: str,
    infile: str,
    outfile: str,
    meta_only: bool,
    **kwargs: dict,
) -> None:
    """
    The ``extract`` subcommand of yadg.

    If ``filetype`` is known to yadg, it will attempt to extract all data from the
    provided ``infile``.

    The data is returned as a :class:`xarray.Dataset` or a datatree, and is stored in
    a NetCDF file. The output location can be configured using the ``outfile``
    argument, by default this is set to the stem of ``infile`` with a ``.nc`` suffix.

    Optionally, an export of just the metadata can be requested by setting the
    ``meta_only`` argument, in this case the output is a json file.

    """
    path = Path(infile)

    assert path.is_file(), (
        f"Supplied object filename '{infile}' does not exist " "or is not a valid file."
    )

    if outfile is None:
        outpath = path.with_suffix(".json" if meta_only else ".nc")
    else:
        outpath = Path(outfile)

    ret = extractors.extract(filetype, path, **kwargs)
    if meta_only:
        meta = _obj_to_meta_dict(ret)
        with outpath.open("w", encoding="UTF-8") as target:
            json.dump(meta, target)
    else:
        ret.to_netcdf(outpath, engine="h5netcdf")
