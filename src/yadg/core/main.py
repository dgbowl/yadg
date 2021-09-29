import argparse
import json
import sys
import os
import logging
from typing import Union, Callable
from importlib import metadata

from parsers import dummy, basiccsv, qftrace, gctrace
from core import validators
import dgutils

def _infer_datagram_handler(parser: str) -> Callable:
    """
    Helper function to distribute work to `parser`s.

    Add your `parser` here.
    """
    if parser == "gctrace":
        return gctrace.process
    if parser == "qftrace":
        return qftrace.process
    #if datagramtype == "meascsv":
    #    return meascsv.process
    if parser == "dummy":
        return dummy.process
    if parser == "basiccsv":
        return basiccsv.process

def _infer_todo_files(importdict: dict) -> list:
    """
    File enumerator function.

    This function enumerates all paths to be processed by yadg using the "import"
    key within a schema step. Currently, the specification allows for folders,
    files or paths.

    Parameters
    ----------
    importdict
        A (dict) describing the paths to process. A valid schema has to contain 
        one, and only one, of the following keys: ``"folders"``, ``"files"``. 
        Additional keys that are processed here are ``"prefix"``, ``"suffix"``, 
        and ``"contains"``.

    Returns
    -------
    todofiles
        A sorted list of paths which match the ``importdict`` spec.
    """
    todofiles = []
    if "folders" in importdict:
        for folder in importdict["folders"]:
            for fn in os.listdir(folder):
                if fn.startswith(importdict.get("prefix", "")) and \
                   fn.endswith(importdict.get("suffix", "")) and \
                   importdict.get("contains", "") in fn: 
                    todofiles.append(os.path.join(folder, fn))
    if "files" in importdict:
        for path in importdict["files"]:
            todofiles.append(path)
    return sorted(todofiles)
                    
def process_schema(schema: Union[list, tuple]) -> dict:
    """
    Main worker function of **yadg**. 
    
    Takes in a validated `schema` as an argument and returns a single annotated 
    `datagram` created from the `schema`. It is the job of the user to supply
    a validated `schema`.

    Parameters
    ----------
    schema
        A fully validated `schema`. Use the function
        :meth:`yadg.core.validators.validate_schema` to validate your `schema`.

    Returns
    -------
    datagram: dict
        An unvalidated `datagram`. The `parser`\ s included in **yadg** should
        return a valid `datagram`; any custom `parser`\ s might not do so. 
        Use the function :meth:`yadg.core.validators.validate_datagram` to 
        validate the resulting `datagram`.
    """
    datagram = {
        "metadata": {
            "yadg": dgutils._yadg_metadata(),
            "date": dgutils.now(asstr=True)
        },
        "data": []
    }
    for step in schema:
        metadata = {
            "input": step.copy(),
            "tag": step["tag"]
        }
        common = {}
        timesteps = []
        logging.info(f'process_schema: processing step {schema.index(step)}:')
        handler = _infer_datagram_handler(step["parser"])
        todofiles = _infer_todo_files(step["import"])
        if len(todofiles) == 0:
            logging.warning(f"process_schema: No files processed by step {step['tag']}")
        for tf in todofiles:
            logging.debug(f'process_schema: processing item {tf}')
            _ts, _meta, _common = handler(tf, **step.get("parameters", {}))
            assert isinstance(_ts, list), \
                logging.critical(f"process_schema: Handler for {step['datagram']} yields"
                                 " timesteps that are not a list.")
            timesteps += _ts
            assert isinstance(_meta, dict) or _meta is None, \
                logging.critical(f"process_schema: Handler for {step['datagram']} yields"
                                 " metadata that are not a dict.")
            if _meta is not None:
                metadata.update(_meta)
            assert isinstance(_common, dict) or _common is None, \
                logging.critical(f"process_schema: Handler for {step['datagram']} yields"
                                 " common data that are not a dict.")
            if _common is not None:
                common.update(_common)
        if common == {}:
            datagram["data"].append({"metadata": metadata, "timesteps": timesteps})
        else:
            datagram["data"].append({"metadata": metadata, "common": common, "timesteps": timesteps})
        if "export" in step and step["export"] is not None:
            with open(step["export"], "w") as ofile:
                json.dump(datagram, ofile, indent=1)
    return datagram

def _parse_arguments() -> argparse.Namespace:
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
                        action="version", version=f'%(prog)s version {metadata.version("yadg")}')
    parser.add_argument("--ignore-file-errors", 
                        dest="permissive", action="store_true",
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
        sys.exit()
    
    assert validators.validate_schema(schema, args.permissive)
    
    datagram = process_schema(schema)
    if args.dump:
        with open(args.dump, "w") as ofile:
            json.dump(datagram, ofile, indent=1)
