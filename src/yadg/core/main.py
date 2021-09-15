import argparse
import json
import sys
import os
import logging

import gctrace
import qftrace
import meascsv
import helpers
import dgutils
from parsers import dummy, basiccsv
from helpers.version import _VERSION


def _infer_datagram_handler(datagramtype):
    if datagramtype == "gctrace":
        return gctrace.process
    if datagramtype == "qftrace":
        return qftrace.process
    if datagramtype == "meascsv":
        return meascsv.process
    if datagramtype == "dummy":
        return dummy.process
    if datagramtype == "basiccsv":
        return basiccsv.process

def _infer_todo_files(importdict, permissive = False):
    """
    File enumerator function.

    This function enumerates all paths to be processed by yadg using the "import"
    key within a schema step. Currently, the specification allows for folders,
    files or paths.

    Parameters
    ----------
    importdict : dict
        Dictionary describing the paths to process. Has to contain one, and only
        one, of the following keys: "folders", "files", "paths". Additional keys
        that are processed here are "prefix", "suffix", and "contains".
    
    permissive : bool, optional
        If true, yadg will not complain if a path specified in `importdict` is 
        not present. Default is false.

    """
    methods = ["folders", "files", "paths"]
    assert len(set(methods) & set(importdict)) == 1, \
        logging.error(f'wrong "import" method specification in importdict: '
                      f'{set(methods) & set(importdict)}')
    todofiles = []
    if "folders" in importdict or "files" in importdict or "paths" in importdict:
        filetype = "file"
    if "files" in importdict:
        importdict["paths"] = importdict.pop("files")
    if "folders" in importdict:
        for folder in importdict["folders"]:
            exists = os.path.exists(folder)
            assert exists or permissive, \
                logging.error(f"Specified folder {folder} doesn't exist.")
            if exists:
                for fn in os.listdir(folder):
                    if fn.startswith(importdict.get("prefix", "")) and \
                       fn.endswith(importdict.get("suffix", "")) and \
                       importdict.get("contains", "") in fn: 
                        todofiles.append(os.path.join(folder, fn))
            else:
                logging.warning(f"Specified folder {folder} doesn't exist.")
    if "paths" in importdict:
        for path in importdict["paths"]:
            exists = os.path.exists(path)
            assert exists or permissive, \
                logging.error(f"Specified path {path} doesn't exist.")
            if exists:
                todofiles.append(path)
            else:
                logging.warning(f"Specified path {path} doesn't exist.")
    return sorted(todofiles), filetype

def _load_resource(resource, resourcetype, **kwargs):
    if resourcetype == "file":
        with open(resource, "r", encoding="utf8", errors='ignore') as infile:
            result = infile.readlines()
    return result

def process_schema(schema, permissive = False):
    """
    Main worker function of `yadg`. 
    
    Takes in a validated `schema` as an argument and returns a single annotated 
    `datagram` created from the `schema`. It is the job of the user to supply
    a validated `schema`.

    Parameters
    ----------
    schema : list
        A fully validated schema
    permissive : bool, optional
        Whether the processor should ignore file errors. 
    """

    tostore = []
    for step in schema:
        data = {
            "input": step.copy(),
            "metadata": {
                "yadg": {
                    "version": _VERSION,
                    "date": helpers.dateutils.now(asstr=True),
                    "command": sys.argv
                }
            }
        }
        logging.info(f'process_schema: processing step {schema.index(step)}:')
        assert "datagram" in step, \
            logging.error('process_schema: No "datagram" field in schema step.')
        assert "import" in step, \
            logging.error('process_schema: No "import" field in schema step.')
        handler = _infer_datagram_handler(step["datagram"])
        todofiles, filetype = _infer_todo_files(step["import"], permissive)
        data["results"] = []
        for tf in todofiles:
            logging.debug(f'process_schema: processing item {tf}')
            ret = handler(tf, **step.get("parameters", {}))
            if isinstance(ret, dict):
                data["results"].append(ret)
            elif isinstance(ret, list): 
                data["results"] += ret
        if len(data["results"]) > 0:
            if data["results"][-1] == None:
                data["results"] = data["results"][:-1]
            if "export" in step and step["export"].lower() not in ["false", "none"]:
                with open(step["export"], "w") as ofile:
                    json.dump(data, ofile, indent=1)
            tostore.append(data)
    print(len(tostore))
    return(tostore)

def _parse_arguments():
    parser = argparse.ArgumentParser(usage = """
        %(prog)s [options] --schemafile [schemafile]
        %(prog)s [options] --preset [preset] --folder [folder]
        """
    )
    parser.add_argument("--schemafile", "--schema", dest="schemafile",
                        help="File containing the schema to be processed by yadg.",
                        default=False)
    parser.add_argument("--dump", "--save", dest="dump",
                        help="Save the created datagram into a specified json file.",
                        default=False)
    parser.add_argument("--preset",
                        help="Specify a schema template from a [preset].")
    parser.add_argument("--folder",
                        help="Specify the folder on which to apply the [preset].")
    parser.add_argument("--version",
                        action="version", version=f'%(prog)s version {_VERSION}')
    parser.add_argument("--ignore-file-errors", 
                        dest="ignore", action="store_true",
                        help='Ignore file opening errors while processing schemafile',
                        default=False)
    parser.add_argument("--log", "--debug", "--loglevel", dest="debug",
                        help="Switch loglevel from WARNING to that provided.",
                        default="warning")
    args = parser.parse_args()
    if not args.schemafile and not (args.preset and args.folder):
        parser.error("Either [schemafile] or [preset] and [folder] have to be supplied.")
    if args.debug.upper() not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
        parser.error(f"{args.debug.upper()} is not a valid loglevel.")
    else:
        logging.basicConfig(level = getattr(logging, args.debug.upper()))
    return args

def run():
    """
    Main execution function.

    This is the function executed when `yadg` is launched using the executable
    or via `python yadg.py`. The function 1) processes the command line 
    arguments, 2) loads or composes the `schema`, 3) validates the `schema`,
    4) processess the `schema` into a `datagram`, and 5) saves the `datagram`
    according to the input.

    """

    args = _parse_arguments()
    if args.schemafile:
        logging.info(f"Processing input json: {args.schemafile}")
        with open(args.schemafile, "r") as infile:
            schema = json.load(infile)
    elif args.folder and args.preset:
        logging.critical("Specifying schema from folder and preset"
                         "is not yet implemented.")
        sys.exit()
    datagram = process_schema(schema)
    if args.dump:
        with open(args.dump, "w") as ofile:
            json.dump(datagram, ofile, indent=1)

            
