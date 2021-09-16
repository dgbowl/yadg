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

def schema_validator(schema, permissive = False):
    """
    Schema validator. 
    
    Checks the overall schema format, checks every schema step for required keys,
    and checks whether required parameters for datagrams are provided.

    The conditions are:
    - schema has to be a list or a tuple
    - each element of this list is a dict, called step
    - each step has to have a "datagram" and "import" entry:
        - the "datagram" entry has to be a string containing the requested parser
        - the "import" entry has to be a dictionary containing:
            - exactly one entry out of "files", "folders", or "paths"
            - any of "prefix", "suffix", "contains" entries
    - other allowed entries are: 
        - "tag" (string) for step tagging,
        - "export" (string) for step export,
        - "parameters" (dict) for specifying other parameters for the parser:
    - no other entries are permitted

    Parameters
    ----------
    schema : list, tuple
        The schema to be validated.
    
    permissive : bool, optional
        When `True`, the files will not be checked for IO errors. Folders are 
        always checked.

    """

    assert isinstance(schema, (list, tuple)), \
        logging.error("schema_validator: Provided schema is neither list nor a tuple.")
    requiredkeys = {
        "datagram": ["dummy", "basiccsv"], 
        "import": {"one": ["files", "folders", "paths"], 
                   "any": ["prefix", "suffix", "contains"]}
    }
    for step in schema:
        si = schema.index(step)
        allowedkeys = {
            "tag": f"{si:03d}", 
            "export": None, 
            "parameters": {}
        }
        assert isinstance(step, dict), \
            logging.error(f"schema_validator: Step {si} of schema is not a dict.")
        assert len(set(requiredkeys.keys()) & set(step.keys())) == len(requiredkeys.keys()), \
            logging.error(f"schema_validator: Step {si} does not contain all "
                          f"required keys: {list(requiredkeys.keys())}")
        for key, vallowed in requiredkeys.items():
            if isinstance(vallowed, list):
                assert step[key] in vallowed, \
                    logging.error(f"schema_validator: Undefined key {step[key]} was"
                                  f"supplied for a required key {key}")
            else:
                assert len(set(step[key]) & set(vallowed["one"])) == 1, \
                    logging.error(f"schema_validator: More than one of exclusive "
                                  f"'{key}' entries {vallowed['one']} was provided.")
                for kkey in step[key]:
                    if kkey in vallowed["one"]:
                        continue
                    assert kkey in vallowed["any"], \
                        logging.error(f"schema_validator: Undefined key {kkey} was"
                                      f"supplied for a required key {key}.")
        if "paths" in step["import"]:
            step["import"]["files"] = step["import"].pop("paths")
        if "files" in step["import"] and not permissive:
            for path in step["import"]["files"]:
                assert os.path.exists(path) and os.path.isfile(path), \
                    logging.error(f"schema_validator: File {path} specified in "
                                  f"'import' of step {si} is not a file.")
        if "folders" in step["import"]:
            for path in step["import"]["folders"]:
                assert os.path.exists(path) and os.path.isdir(path), \
                    logging.error(f"schema_validator: Folder {path} specified in "
                                  f"'import' of step {si} is not a folder.")
        for key, kdef in allowedkeys.items():
            if key in step:
                assert isinstance(step[key], type(kdef)) or step[key] is None, \
                    logging.error(f"schema_validator: Step {si} contains {key} of "
                                  f"the wrong type {type(step[key])}.")
            if key not in step or step[key] is None:
                step[key] = kdef



def _infer_todo_files(importdict):
    """
    File enumerator function.

    This function enumerates all paths to be processed by yadg using the "import"
    key within a schema step. Currently, the specification allows for folders,
    files or paths.

    Parameters
    ----------
    importdict : dict
        Dictionary describing the paths to process. A valid schema has to contain 
        one, and only one, of the following keys: "folders", "files". Additional 
        keys that are processed here are "prefix", "suffix", and "contains".

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

def process_schema(schema):
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
        todofiles = _infer_todo_files(step["import"])
        if len(todofiles) == 0:
            logging.warning("process_schema: ")
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
            if "export" in step and step["export"] is not None:
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

    This is the function executed when `yadg` is launched using the executable
    or via `python yadg.py`. The function 1) processes the command line 
    arguments, 2) loads or composes the `schema`, 3) validates the `schema`,
    4) processess the `schema` into a `datagram`, and 5) saves the `datagram`
    according to the input.

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
    
    schema_validator(schema, args.permissive)
    
    datagram = process_schema(schema)
    if args.dump:
        with open(args.dump, "w") as ofile:
            json.dump(datagram, ofile, indent=1)

            
