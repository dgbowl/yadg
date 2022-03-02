import os
import argparse
import logging
import json
from . import core, dgutils


logger = logging.getLogger(__name__)


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

    logger.info("Reading input json from '%s'.", args.infile)
    with open(args.infile, "r") as infile:
        schema = json.load(infile)

    logger.debug("Validating schema.")
    assert core.validate_schema(schema, args.permissive)

    logger.debug("Processing schema")
    datagram = core.process_schema(schema)

    logger.info("Saving datagram to '%s'.", args.outfile)
    with open(args.outfile, "w") as ofile:
        json.dump(datagram, ofile, indent=1)


def update(args: argparse.Namespace) -> None:
    """
    The ``update`` subcommand of **yadg**.

    This function requires the ``args.type`` argument, which defines whether the
    object to be updated is a `datagram` or a `schema`. Generally, updating a
    `schema` and then re-processing the raw data is preferred to updating a
    `datagram`.

    If the supplied ``args.infile`` exists, and can be parsed as a json, it will
    be passed to :func:`yadg.dgutils.update_object` to perform the update. If the
    update is successful, the object is checked for validity and written out
    into ``args.outfile`` (which is the ``args.infile`` with  a `".new.json"`
    suffix by default).
    """
    assert args.type in ["datagram", "schema"], (
        f"Specified object type '{args.type}' is not one of " "['datagram', 'schema']."
    )

    assert os.path.exists(args.infile) and os.path.isfile(args.infile), (
        f"Supplied object filename '{args.infile}' does not exist "
        "or is not a valid file."
    )

    logger.info("Reading input json from '%s'.", args.infile)
    with open(args.infile) as infile:
        inobj = json.load(infile)

    if args.outfile is None:
        name, ext = os.path.splitext(args.infile)
        args.outfile = f"{name}.new.json"

    logger.info("Updating old object.")
    outobj = dgutils.update_object(args.type, inobj)

    logger.info("Writing new object into '%s'.", args.outfile)
    with open(args.outfile, "w") as outfile:
        json.dump(outobj, outfile, indent=1)


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

    logger.info("Reading input json from '%s'.", args.preset)
    with open(args.preset) as infile:
        preset = json.load(infile)

    logger.info("Validating loaded preset.")
    assert core.validate_schema(preset, strictfiles=False, strictfolders=False)

    logger.info("Creating a schema from preset for '{args.folder}'.")
    schema = dgutils.schema_from_preset(preset, args.folder)

    logger.info("Validating created schema.")
    assert core.validate_schema(schema)

    if args.process:
        logger.info("Processing created schema.")
        datagram = core.process_schema(schema)
        args.outfile = "datagram.json" if args.outfile is None else args.outfile
        logger.info("Saving datagram to '%s'.", args.outfile)
        with open(args.outfile, "w") as ofile:
            json.dump(datagram, ofile, indent=1)
    else:
        args.outfile = "schema.json" if args.outfile is None else args.outfile
        logger.info("Saving schema to '%s'.", args.outfile)
        with open(args.outfile, "w") as ofile:
            json.dump(schema, ofile, indent=1)
