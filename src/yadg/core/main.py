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
from parsers import dummy
from helpers.version import _VERSION


def _inferDatagramHandler(datagramtype):
    if datagramtype == "gctrace":
        return gctrace.process
    if datagramtype == "qftrace":
        return qftrace.process
    if datagramtype == "meascsv":
        return meascsv.process
    if datagramtype == "dummy":
        return dummy.process
    

def _inferTodoFiles(importdict, permissive = False, **kwargs):
    methods = ["folders", "files", "paths"]
    assert len(set(methods) & set(importdict)) == 1, \
        f'YADG: wrong "import" method specification in importdict: {set(methods) & set(importdict)}'
    todofiles = []
    if "folders" in importdict or "files" in importdict or "paths" in importdict:
        filetype = "file"
    if "folders" in importdict:
        for folder in importdict["folders"]:
            try:
                assert os.path.exists(folder) or permissive, \
                    f"YADG: folder {folder} doesn't exist"
                for fn in os.listdir(folder):
                    if fn.startswith(importdict.get("prefix", "")) and \
                    fn.endswith(importdict.get("suffix", "")):
                        todofiles.append(os.path.join(folder, fn))
            except FileNotFoundError:
                if permissive:
                    pass
    if "files" in importdict:
        importdict["paths"] = importdict.pop("files")
    if "paths" in importdict:
        for path in importdict["paths"]:
            if not permissive:
                assert os.path.exists(path), \
                    f"YADG: file {path} doesn't exist"
            todofiles.append(path)
    return sorted(todofiles), filetype

def _loadResource(resource, resourcetype, **kwargs):
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
                    "date": helpers.dateutils.now(asstr=True)
                }
            }
        }
        logging.info(f'YADG: processing step {schema.index(step)}:')
        assert "datagram" in step, \
            f'YADG: no "datagram" field in schema step.'
        assert "import" in step, \
            f'YADG: no "import" field in schema step.'
        handler = _inferDatagramHandler(step["datagram"])
        todofiles, filetype = _inferTodoFiles(step["import"], permissive)
        data["results"] = []
        for tf in todofiles:
            logging.debug(f'YADG: processing item {tf}')
            ret = handler(tf, **step.get("parameters", {}))
            if isinstance(ret, dict):
                data["results"].append(ret)
            elif isinstance(ret, list): 
                data["results"] += ret
        if len(data["results"]) > 0:
            if data["results"][-1] == None:
                data["results"] = data["results"][:-1]
            if "export" not in step or step["export"].lower() in ["false", "none"]:
                pass
            else:
                with open(step["export"], "w") as ofile:
                    json.dump(data, ofile, indent=1)
            tostore.append(data)
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

            
