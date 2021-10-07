#!/usr/bin/env python
import argparse
import sys
import os
import logging
from importlib import metadata
import json

import yadg.core

def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("schemafile", nargs = "?", 
                        help="File containing the schema to be processed by yadg.",
                        default=None)
    parser.add_argument("--schemafile", "--schema", dest="infile",
                        help="File containing the schema to be processed by yadg.",
                        default=False)
    parser.add_argument("datagramfile", nargs = "?", 
                        help="Output file to save the created datagram to.",
                        default=None)
    parser.add_argument("--dump", "--saveas", dest="outfile",
                        help="Output file to save the created datagram to.",
                        default=False)
    parser.add_argument("--preset",
                        help="Specify a schema template from a [preset].")
    parser.add_argument("--folder",
                        help="Specify the folder on which to apply the [preset].")
    parser.add_argument("--version",
                        action="version", version=f'%(prog)s version {metadata.version("yadg")}')
    parser.add_argument("--ignore-file-errors", 
                        dest="permissive", action="store_true",
                        help='Ignore file opening errors while processing schemafile',
                        default=False)
    parser.add_argument("--log", "--debug", "--loglevel", dest="debug",
                        help="Switch loglevel from WARNING to that provided.",
                        default="warning")
    args = parser.parse_args()
    if args.schemafile is None:
        args.schemafile = args.infile
    if args.datagramfile is None:
        args.datagramfile = args.outfile if args.outfile else "datagram.json"
    if not args.schemafile and not (args.preset and args.folder):
        parser.error("Either [schemafile] or [preset] and [folder] have to be supplied.")
    if not (os.path.exists(args.schemafile) and os.path.isfile(args.schemafile)):
        parser.error("Supplied [schemafile] does not exist.")
    if args.debug.upper() not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
        parser.error(f"{args.debug.upper()} is not a valid loglevel.")
    else:
        logging.basicConfig(level = getattr(logging, args.debug.upper()))
    return args

def run():
    """
    Main execution function.

    This is the function executed when **yadg** is launched using the executable
    or via `python yadg.py`. The function: 
    
      1) processes the command line arguments into ``args``, 
      2) loads or composes the `schema` based on ``args``, 
      3) validates the `schema`,
      4) processes the `schema` into a `datagram`, and 
      5) saves the `datagram` into a ``json`` file according to the ``args``.

    """
    args = _parse_arguments()
    if args.schemafile:
        logging.info(f"run: Processing input json: {args.schemafile}")
        with open(args.schemafile, "r") as infile:
            schema = json.load(infile)
    elif args.folder and args.preset:
        logging.critical("run: Specifying schema from folder and preset"
                         "is not yet implemented.")
        sys.exit(1)
    
    logging.debug("run: Validating schema.")
    assert yadg.core.validate_schema(schema, args.permissive)
    logging.debug("run: Processing schema")
    datagram = yadg.core.process_schema(schema)
    if args.datagramfile:
        logging.info(f"run: Saving data to {args.datagramfile}")
        with open(args.datagramfile, "w") as ofile:
            json.dump(datagram, ofile, indent=1)

if __name__ == "__main__":
    run()    
