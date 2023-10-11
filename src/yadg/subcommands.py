import os
import argparse
import logging
import json
import yaml
import shutil
import hashlib
from pathlib import Path

# from dgbowl_schemas import to_dataschema
from dgbowl_schemas.yadg import to_dataschema
from . import core, dgutils, extractors


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


def process(args: argparse.Namespace) -> None:
    """
    The ``process`` subcommand of **yadg**.

    This function first checks that the supplied ``args.infile`` exists, is a valid
    `schema`, and if yes, proceeds to process the `schema` into a `datagram`. If
    this is successful, the `datagram` is checked for validity and written out
    into ``args.outfile`` (which is `"datagram.json"` by default).
    """
    assert os.path.exists(args.infile) and os.path.isfile(args.infile), (
        f"Supplied schema filename '{args.infile}' does not exist "
        "or is not a valid file."
    )

    logger.info("Reading input file from '%s'.", args.infile)
    schema = _load_file(args.infile)

    logger.info("Loading dataschema.")
    ds = to_dataschema(**schema)
    logger.info("Loaded dataschema version '%s'", ds.metadata.version)

    while hasattr(ds, "update"):
        ds = ds.update()

    logger.debug("Processing schema")
    datagram = core.process_schema(ds, strict_merge=not args.ignore_merge_errors)

    logger.info("Saving datagram to '%s'.", args.outfile)
    datagram.to_netcdf(args.outfile, engine="h5netcdf")
    # with open(args.outfile, "w") as ofile:
    #    json.dump(datagram, ofile, indent=1)


def update(args: argparse.Namespace) -> None:
    """
    The ``update`` subcommand of **yadg**.

    This function updates the `DataSchema` present in the ``args.infile`` argument to
    comply with the newest version of `DataSchema`, and saves the resulting object into
    ``args.outfile`` (which is the ``args.infile`` with  a `".new.json"` suffix
    by default).
    """

    assert os.path.exists(args.infile) and os.path.isfile(args.infile), (
        f"Supplied object filename '{args.infile}' does not exist "
        "or is not a valid file."
    )

    logger.info("Reading input file from '%s'.", args.infile)
    inobj = _load_file(args.infile)

    if args.outfile is None:
        name, ext = os.path.splitext(args.infile)
        args.outfile = f"{name}.new.json"

    outobj = dgutils.update_schema(inobj)

    logger.info("Writing new object into '%s'.", args.outfile)
    with open(args.outfile, "w") as outfile:
        json.dump(outobj.dict(), outfile, indent=1)


def preset(args: argparse.Namespace) -> None:
    """
    The ``preset`` subcommand of **yadg**.

    This function requires the ``args.preset`` and ``args.folder`` arguments.
    If ``args.folder`` is an existing folder and ``args.preset`` a valid `schema`
    file (with appropriately formated ``"import"`` and ``"calfile"`` entries),
    this function will prepend the specified ``args.folder`` to all paths in the
    ``args.preset``, convert them to absolute paths, and save the resulting `schema`
    in the supplied ``args.outfile``.

    Alternatively, if ``args.process`` is specified, the created `schema` will be
    directly processed into a `datagram`, which is then saved in ``args.outfile``.
    """
    assert os.path.exists(args.folder) and os.path.isdir(args.folder), (
        f"Supplied folder path '{args.folder}' does not exist "
        "or is not a valid folder."
    )

    if not os.path.isabs(args.folder) and not args.process:
        logger.warning(
            "The provided path '%s' is a relative path. The generated schema "
            "likely will not work outside current working directory.",
            args.folder,
        )

    assert os.path.exists(args.preset) and os.path.isfile(args.preset), (
        f"Supplied preset path '{args.preset}' does not exist "
        "or is not a valid file."
    )

    logger.info("Reading input file from '%s'.", args.preset)
    preset = _load_file(args.preset)

    logger.info("Processing preset as schema.")
    schema = to_dataschema(**preset)

    logger.info("Creating a schema from preset for '%s'.", args.folder)
    ds = dgutils.schema_from_preset(schema, args.folder)

    logger.info("Loaded dataschema version '%s'", ds.metadata.version)
    if args.process:
        logger.info("Processing created schema.")
        datagram = core.process_schema(ds, strict_merge=not args.ignore_merge_errors)
        args.outfile = "datagram.nc" if args.outfile is None else args.outfile
        if args.archive:
            zipfile = args.outfile.replace(".nc", "")
            logger.info("Zipping input folder into '%s'", zipfile)
            fn, hash = _zip_file(args.folder, zipfile, method=args.packwith)
            datagram.attrs["data_archive_sha-1"] = hash
            datagram.attrs["data_archive_path"] = fn
        logger.info("Saving datagram to '%s'.", args.outfile)
        datagram.to_netcdf(args.outfile, engine="h5netcdf")
    else:
        if args.archive:
            logger.warning(
                "The --archive option must be supplied along with --process. "
                "Continuing without archiving."
            )
        args.outfile = "schema.json" if args.outfile is None else args.outfile
        logger.info("Saving schema to '%s'.", args.outfile)
        with open(args.outfile, "w") as ofile:
            json.dump(ds.dict(), ofile, indent=1)


def extract(args: argparse.Namespace) -> None:
    """
    The ``extract`` subcommand of **yadg**.

    This function requires the ``args.filetype`` and ``args.infile`` positional arguments.
    If ``args.filetype`` (or it's namespaced version, such as ``marda:{args.filetype}``)
    is a known :class:`FileType`, ``yadg`` will attempt to extract metadata and data from
    the provided ``args.infile``.

    The data is returned as a NetCDF file. The location can be configured using the
    ``args.outfile`` parameter, by default this is set to the stem of ``args.infile`` with
    a ``.nc`` suffix.
    """

    path = Path(args.infile)

    assert path.is_file(), (
        f"Supplied object filename '{args.infile}' does not exist "
        "or is not a valid file."
    )

    if args.outfile is None:
        outpath = path.with_suffix(".json" if args.meta_only else ".nc")
    else:
        outpath = Path(args.outfile)

    ret = extractors.extract(args.filetype, path)
    if args.meta_only:
        with outpath.open("w", encoding="UTF-8") as target:
            json.dump(ret.to_dict(data=False), target)
    else:
        ret.to_netcdf(outpath, engine="h5netcdf")
