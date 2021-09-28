import argparse
import json
import sys
import os
import logging
from typing import Union, Callable

from parsers import dummy, basiccsv, qftrace, gctrace
from helpers.version import _VERSION
from helpers import dateutils
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

def schema_validator(schema: Union[list, tuple], strictfiles: bool = False) -> True:
    """
    Schema validator. 
    
    Checks the overall `schema` format, checks every `step` of the `schema` for 
    required entries, and checks whether required parameters for each `parser` 
    are provided.

    The specification is:
    
    - The `schema` has to be (Union[list, tuple])
    - Each element of this parent list is a `step` (dict)
    - Each `step` has to have the ``"parser"`` and ``"import"`` entries:
    
      - The ``"parser"`` (str) entry has contain the name of the requested 
        parser module. This entry is processed in the :meth:`_infer_datagram_handler`
        function in this module.
      - The ``"import"`` (dict) entry has to contain:
      
        - Exactly **one** entry out of ``"files"``, ``"folders"``, or ``"paths"``.
          This entry must be a (list) even if only one element is provided. 
        - Any combination of ``"prefix"``, ``"suffix"``, ``"contains"`` entries,
          which must be a (str). These entries specify the matching of files 
          within folders accordingly.
        
    - The only other allowed entries are:
    
      - ``"tag"`` (str): for defining a tag for each `step`; by default assigned
        the numerical index of the `step` within the `schema`.
      - ``"export"`` (str): for `step` export; if the processed `step` should be
        exported as a ``json`` file which is kept available for other `step`\ s
      - ``"parameters"`` (dict): for specifying other parameters for the parser.
      
    - no other entries are permitted

    Parameters
    ----------
    schema
        The schema to be validated.
    
    strictfiles
        When `True`, the files will not be checked for IO errors. Folders are 
        always checked.
    
    Returns
    -------
    True: bool
        When the `schema` is valid and passes all assertions, `True` is returned.
    """
    # schema has to be a list or a tuple
    assert isinstance(schema, (list, tuple)), \
        logging.error("schema_validator: Provided schema is neither list nor a tuple.")
    requiredkeys = {
        "parser": {
            "one": ["dummy", "basiccsv", "qftrace", "gctrace"],
            "any": []
        }, 
        "import": {
            "one": ["files", "folders", "paths"], 
            "any": ["prefix", "suffix", "contains"]
        }
    }
    for step in schema:
        si = schema.index(step)
        allowedkeys = {
            "tag": f"{si:03d}", 
            "export": None, 
            "parameters": {}
        }
        # step in a schema has to be a dict
        assert isinstance(step, dict), \
            logging.error(f"schema_validator: Step {si} of schema is not a dict.")
        # all required keys have to be in a step
        assert len(set(requiredkeys.keys()) & set(step.keys())) == len(requiredkeys.keys()), \
            logging.error(f"schema_validator: Step {si} does not contain all "
                          f"required keys: {list(requiredkeys.keys())}")
        for kreq, vreq in requiredkeys.items():
            # exactly one of entries in "one" must be present
            assert (isinstance(step[kreq], str) and step[kreq] in vreq["one"]) or \
                   (isinstance(step[kreq], dict) and len(set(step[kreq]) & set(vreq["one"])) == 1), \
                logging.error(f"schema_validator: More than one of exclusive "
                              f"'{kreq}' entries from {vreq['one']} was provided.")
            # additionally, only entries in "any" are present
            if isinstance(step[kreq], dict):
                for key in step[kreq]:
                    if key in vreq["one"]:
                        continue
                    assert key in vreq["any"], \
                        logging.error(f"schema_validator: Undefined entry {key} was"
                                      f"supplied as a parameter for a required key {kreq}.")
        # validate "import" spec
        if "paths" in step["import"]:
            step["import"]["files"] = step["import"].pop("paths")
        if "files" in step["import"] and not strictfiles:
            for path in step["import"]["files"]:
                assert os.path.exists(path) and os.path.isfile(path), \
                    logging.error(f"schema_validator: File {path} specified in "
                                  f"'import' of step {si} is not a file.")
        if "folders" in step["import"]:
            for path in step["import"]["folders"]:
                assert os.path.exists(path) and os.path.isdir(path), \
                    logging.error(f"schema_validator: Folder {path} specified in "
                                  f"'import' of step {si} is not a folder.")
        # additionally, only entries in allowedkeys are permitted; fill defaults
        for key, kdef in allowedkeys.items():
            if key in step:
                assert isinstance(step[key], type(kdef)) or step[key] is None, \
                    logging.error(f"schema_validator: Step {si} contains {key} of "
                                  f"the wrong type {type(step[key])}.")
            if key not in step or step[key] is None:
                step[key] = kdef
        # validate supplied parameters
        for key, val in step["parameters"].items():
            # validation of "timestamp" spec
            if key == "timestamp":
                assert isinstance(val, dict), \
                    logging.error(f"schema_validator: Value of {key} in 'parameters'"
                                  f" of step {si} is not a dict.")
                allowedtimestamps = ["uts", "timestamp", "date", "time"]
                for k, v in val.items():
                    assert k in allowedtimestamps, \
                        logging.error("schema_validator: timestamp has to be one of "
                                      f"{allowedtimestamps}, not {k}.")
                    assert (isinstance(v, (tuple, list)) and len(v) == 2) or isinstance(v, int), \
                        logging.error("schema_validator: timestamp specification has"
                                      "to be column index (int), or a tuple/list "
                                      "with a column index (int) and format (string).")
    return True
                    
def process_schema(schema: Union[list, tuple]) -> dict:
    """
    Main worker function of **yadg**. 
    
    Takes in a validated `schema` as an argument and returns a single annotated 
    `datagram` created from the `schema`. It is the job of the user to supply
    a validated `schema`.

    Parameters
    ----------
    schema
        A fully validated schema

    Returns
    -------
    datagram: dict
        A fully qualified datagram, including toplevel metadata.
    """
    datagram = {
        "metadata": {
            "yadg": dgutils._yadg_metadata(),
            "date": dateutils.now(asstr=True)
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
    
    schema_validator(schema, args.permissive)
    
    datagram = process_schema(schema)
    if args.dump:
        with open(args.dump, "w") as ofile:
            json.dump(datagram, ofile, indent=1)
