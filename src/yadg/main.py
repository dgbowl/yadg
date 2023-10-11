#!/usr/bin/env python
import argparse
import logging
from importlib import metadata
import requests
import json
from packaging import version
from . import subcommands

logger = logging.getLogger(__name__)


def version_check(project="yadg"):
    url = f"https://pypi.org/pypi/{project}/json"
    try:
        res = requests.get(url, timeout=1)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        logger.debug(f"Version check could not proceed due to Exception={e}.")
        return
    jsdata = json.loads(res.text)
    versions = sorted([version.parse(i) for i in jsdata["releases"].keys()])
    latest = versions[-1]
    current = version.parse(metadata.version(project))
    if latest > current:
        logger.warning("You are using an out-of-date version of '%s'. ", project)
        logger.info(
            "The latest version is '%s', the current version is '%s'.", latest, current
        )
        logger.info(
            "Consider updating using: pip install --upgrade %s==%s", project, latest
        )
    else:
        logger.debug("Your version of '%s' is up-to-date.", project)


def set_loglevel(delta: int):
    loglevel = min(max(30 - (10 * delta), 10), 50)
    logging.basicConfig(level=loglevel)
    logger.debug("loglevel set to '%s'", logging._levelToName[loglevel])


def run_with_arguments():
    """
    Main execution function.

    This is the function executed when **yadg** is launched using the executable.
    The function has three subcommands:

    - ``process``: processes a given schema into a datagram.
    - ``update``: updates a given schema or datagram to the current version.
    - ``preset``: creates a schema from a preset file and a target folder.

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
        help="File containing the schema to be processed by yadg.",
        default=None,
    )
    process.add_argument(
        "outfile",
        nargs="?",
        help="Output file to save the created datagram to.",
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
        help="The file containing the schema in the old format.",
    )
    update.add_argument(
        "outfile",
        nargs="?",
        help="Output file to save the updated object to.",
        default=None,
    )
    update.set_defaults(func=subcommands.update)

    preset = subparsers.add_parser("preset")
    preset.add_argument(
        "-p",
        "--process",
        action="store_true",
        help="Immediately process the schema created from the preset.",
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
        help="Specify a schema template from a 'preset'.",
    )
    preset.add_argument(
        "folder",
        help="Specify the 'folder' on which to apply the 'preset'.",
    )
    preset.add_argument(
        "outfile",
        nargs="?",
        help=(
            "Output file to save the created schema file. Default is 'schema.json'. "
            "If '--process' is specified, the created datagram file will be saved "
            "instead. Default in that case is 'datagram.nc'."
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
        help="Specify the filetype to select the appropriate extractor.",
    )
    extract.add_argument(
        "infile",
        help="Specify the 'infile' which should be extracted.",
    )
    extract.add_argument(
        "outfile",
        nargs="?",
        help=("Optionally specify the output file name."),
        default=None,
    )
    extract.add_argument(
        "--meta-only",
        "-m",
        action="store_true",
        help="Extract and return file metadata only in a JSON format.",
        default=False,
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

    version_check()

    if "func" in args:
        args.func(args)
