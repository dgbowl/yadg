#!/usr/bin/env python
import argparse
import logging
from importlib import metadata

from yadg import subcommands

logger = logging.getLogger(__name__)


def set_loglevel(delta: int):
    loglevel = min(max(30 - (10 * delta), 10), 50)
    logging.basicConfig(level=loglevel)
    logger.debug("loglevel set to '%s'", logging._levelToName[loglevel])


def run_with_arguments():
    """
    Main execution function.

    This is the function executed when yadg is launched via its executable.
    The function has the following subcommands:

    - ``extract``: extracts (meta)data from a given file.
    - ``process``: processes a given dataschema, extracting data into a NetCDF file.
    - ``update``: updates a given dataschema to the current version.
    - ``preset``: creates a dataschema from a preset file and a target folder.

    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--version",
        action="version",
        version=f'%(prog)s version {metadata.version("yadg")}',
    )

    verbose = argparse.ArgumentParser(add_help=False)

    for p in [parser, verbose]:
        p.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="Increase verbosity by one level.",
        )
        p.add_argument(
            "--quiet",
            "-q",
            action="count",
            default=0,
            help="Decrease verbosity by one level.",
        )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    process = subparsers.add_parser("process")
    process.add_argument(
        "infile",
        help="File containing the dataschema to be processed by yadg.",
        default=None,
    )
    process.add_argument(
        "outfile",
        nargs="?",
        help="Output NetCDF file to save the created datatree to.",
        default="datagram.nc",
    )
    process.add_argument(
        "--ignore-merge-errors",
        dest="ignore_merge_errors",
        action="store_true",
        help="Ignore metadata merge errors while processing multiple files in a step.",
        default=False,
    )
    process.set_defaults(func=subcommands.process)

    update = subparsers.add_parser("update")
    update.add_argument(
        "infile",
        help="The file containing the dataschema in the old format.",
    )
    update.add_argument(
        "outfile",
        nargs="?",
        help="Output file to save the updated dataschema to.",
        default=None,
    )
    update.set_defaults(func=subcommands.update)

    preset = subparsers.add_parser("preset")
    preset.add_argument(
        "-p",
        "--process",
        action="store_true",
        help="Immediately process the dataschema created from the preset.",
        default=False,
    )
    preset.add_argument(
        "-a",
        "--archive",
        action="store_true",
        help="Archive the whole preset folder after processing.",
        default=False,
    )
    preset.add_argument(
        "--packwith",
        nargs="?",
        choices=["zip", "tar", "bztar", "xztar", "gztar"],
        help="Select compression algorithm for --archive.",
        default="zip",
    )
    preset.add_argument(
        "preset",
        help="Specify a preset, i.e. a dataschema template.",
    )
    preset.add_argument(
        "folder",
        help="Specify the folder on which to apply the preset.",
    )
    preset.add_argument(
        "outfile",
        nargs="?",
        help=(
            "Output file for the created dataschema file. Default is 'schema.json'. "
            "If '--process' is specified, the created datatree will be saved instead. "
            "Default in that case is 'datagram.nc'."
        ),
        default=None,
    )
    preset.add_argument(
        "--ignore-merge-errors",
        dest="ignore_merge_errors",
        action="store_true",
        help="Ignore metadata merge errors while processing multiple files in a step.",
        default=False,
    )
    preset.set_defaults(func=subcommands.preset)

    extract = subparsers.add_parser("extract")
    extract.add_argument(
        "filetype",
        help="Specify the filetype of the infile, selecting an appropriate extractor.",
    )
    extract.add_argument(
        "infile",
        help="Specify the input file which should be extracted.",
    )
    extract.add_argument(
        "outfile",
        nargs="?",
        help="Specify the output file name.",
        default=None,
    )
    extract.add_argument(
        "--meta-only",
        "-m",
        action="store_true",
        help="Extract and return file metadata only in a JSON format.",
        default=False,
    )
    extract.add_argument(
        "--locale",
        help="Set locale of the extracted file.",
        default=None,
        type=str,
    )
    extract.add_argument(
        "--encoding",
        help="Set encoding of the extracted file.",
        default=None,
        type=str,
    )
    extract.add_argument(
        "--timezone",
        help="Set timezone for the extracted file.",
        default=None,
        type=str,
    )
    extract.set_defaults(func=subcommands.extract)

    # parse subparser args
    args, extras = parser.parse_known_args()
    # parse extras for verbose tags
    args, extras = verbose.parse_known_args(extras, args)
    # assign last extra to outfile
    if len(extras) == 1:
        args.outfile = extras[0]

    set_loglevel(args.verbose - args.quiet)

    if "func" in args:
        args.func(**vars(args))
