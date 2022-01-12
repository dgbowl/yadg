#!/usr/bin/env python
import argparse
import os
import logging
from importlib import metadata

import yadg.subcommands


def set_loglevel(delta: int):
    loglevel = min(max(30 - (10 * delta), 10), 50)
    logging.basicConfig(level=loglevel)
    logging.debug(f"loglevel set to '{logging._levelToName[loglevel]}'")

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
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Increase verbosity by one level.",
        )
        p.add_argument(
            "-q",
            "--quiet",
            action="count",
            default=0,
            help="Decrease verbosity by one level.",
        )

    subparsers = parser.add_subparsers(dest="subcommand", required = True)

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
        default="datagram.json",
    )
    process.add_argument(
        "--ignore-file-errors",
        dest="permissive",
        action="store_true",
        help="Ignore file opening errors while processing schemafile",
        default=False,
    )
    process.set_defaults(func=yadg.subcommands.process)

    update = subparsers.add_parser("update")
    update.add_argument(
        "type",
        choices=["schema", "datagram"],
        help="Specify whether a schema or a datagram is to be expected.",
    )
    update.add_argument(
        "infile",
        help="The file containing the schema/datagram in the old format.",
    )
    update.add_argument(
        "outfile",
        nargs="?",
        help="Output file to save the updated object to.",
        default=None,
    )
    update.set_defaults(func=yadg.subcommands.update)

    preset = subparsers.add_parser("preset")
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
            "instead. Default in that case is 'datagram.json'."
        ),
        default=None,
    )
    preset.add_argument(
        "--process",
        "-p",
        action="store_true",
        help="Immediately process the schema created from the preset.",
        default=False,
    )
    preset.set_defaults(func=yadg.subcommands.preset)
        
    # parse subparser args
    args, extras = parser.parse_known_args()
    # parse extras for verbose tags
    args, extras = verbose.parse_known_args(extras, args)
    
    set_loglevel(args.verbose - args.quiet)
    if "func" in args:
        args.func(args)
