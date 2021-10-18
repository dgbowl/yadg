
import json
import os
import logging
from typing import Union, Callable

from parsers import dummy, basiccsv, qftrace, gctrace, drycal
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
    if parser == "drycal":
        return drycal.process

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
            "provenance": {
                "yadg": dgutils.get_yadg_metadata(),
            },
            "date": dgutils.now(asstr=True),
            "input_schema": schema.copy(),
            "datagram_version": "0.1"
        },
        "data": []
    }
    for step in schema["steps"]:
        metadata = {
            "tag": step["tag"]
        }
        common = {}
        timesteps = []
        logging.info(f'process_schema: processing step {schema["steps"].index(step)}:')
        handler = _infer_datagram_handler(step["parser"])
        todofiles = _infer_todo_files(step["import"])
        encoding = step["import"].get("encoding", "utf-8")
        if len(todofiles) == 0:
            logging.warning(f"process_schema: No files processed by step {step['tag']}")
        for tf in todofiles:
            logging.debug(f'process_schema: processing item {tf}')
            _ts, _meta, _common = handler(tf, encoding, **step.get("parameters", {}))
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



