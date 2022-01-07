import json
import os
import logging
from typing import Union, Callable

from yadg.parsers import (
    dummy,
    basiccsv,
    qftrace,
    chromtrace,
    flowdata,
    meascsv,
    electrochem,
    masstrace,
)
import yadg.dgutils
import yadg.core


def _infer_datagram_handler(parser: str) -> tuple[Callable, str]:
    """
    Helper function to distribute work to `parser`s.

    Add your `parser` here.

    Parameters
    ----------
    parser
        Name of the parser from schema.

    Returns
    -------
    (process, version): tuple[Callable, str]
        A tuple containing the handler function as :class:`(Callable)` and the handler
        version as :class:`(str)`.
    """
    if parser == "chromtrace":
        return chromtrace.process, chromtrace.version
    if parser == "qftrace":
        return qftrace.process, qftrace.version
    if parser == "dummy":
        return dummy.process, dummy.version
    if parser == "basiccsv":
        return basiccsv.process, basiccsv.version
    if parser == "flowdata":
        return flowdata.process, flowdata.version
    if parser == "meascsv":
        return meascsv.process, meascsv.version
    if parser == "electrochem":
        return electrochem.process, electrochem.version
    if parser == "masstrace":
        return masstrace.process, masstrace.version


def _infer_todo_files(importdict: dict) -> list:
    """
    File enumerator function.

    This function enumerates all paths to be processed by yadg using the "import" key
    within a schema step. Currently, the specification allows for folders, files or paths.

    Parameters
    ----------
    importdict
        A (dict) describing the paths to process. A valid schema has to contain one, and
        only one, of the following keys: ``"folders"``, ``"files"``. Additional keys
        that are processed here are ``"prefix"``, ``"suffix"``, and ``"contains"``.

    Returns
    -------
    todofiles
        A sorted list of paths which match the ``importdict`` spec.
    """
    todofiles = []
    if "folders" in importdict:
        for folder in importdict["folders"]:
            for fn in os.listdir(folder):
                if (
                    fn.startswith(importdict.get("prefix", ""))
                    and fn.endswith(importdict.get("suffix", ""))
                    and importdict.get("contains", "") in fn
                ):
                    todofiles.append(os.path.join(folder, fn))
    if "files" in importdict:
        for path in importdict["files"]:
            todofiles.append(path)
    return sorted(todofiles)


def process_schema(schema: Union[list, tuple]) -> dict:
    """
    Main worker function of **yadg**.

    Takes in a validated `schema` as an argument and returns a single annotated
    `datagram` created from the `schema`. It is the job of the user to supply a
    validated `schema`.

    Parameters
    ----------
    schema
        A fully validated `schema`. Use the function :meth:`yadg.core.validators.validate_schema`
        to validate your `schema`.

    Returns
    -------
    datagram: dict
        An unvalidated `datagram`. The `parser`\\ s included in **yadg** should return
        a valid `datagram`; any custom `parser`\\ s might not do so. Use the function
        :meth:`yadg.core.validators.validate_datagram` to validate the resulting `datagram`.
    """
    datagram = {
        "metadata": {
            "provenance": {"yadg": yadg.dgutils.get_yadg_metadata(),},
            "date": yadg.dgutils.now(asstr=True),
            "input_schema": schema.copy(),
            "datagram_version": yadg.core.spec_datagram.datagram_version,
        },
        "steps": [],
    }
    for step in schema["steps"]:
        metadata = dict()
        common = dict()
        timesteps = list()
        logging.info(f'process_schema: processing step {schema["steps"].index(step)}:')
        handler, parserversion = _infer_datagram_handler(step["parser"])
        metadata["tag"] = step.get("tag", f"{schema['steps'].index(step):02d}")
        metadata["parser"] = {step["parser"]: {"version": parserversion}}
        todofiles = _infer_todo_files(step["import"])
        if len(todofiles) == 0:
            logging.warning(
                f"process_schema: No files processed by step {metadata['tag']}"
            )
        for tf in todofiles:
            logging.debug(f"process_schema: processing item {tf}")
            ts, meta, comm = handler(
                tf,
                encoding=step["import"].get("encoding", "utf-8"),
                timezone=schema["metadata"].get("timezone", "localtime"),
                **step.get("parameters", {}),
            )
            assert isinstance(
                ts, list
            ), f"process_schema: Handler for {step['parser']} yields timesteps that are not a enclosed in a `list`."
            timesteps += ts
            assert (
                isinstance(meta, dict) or meta is None
            ), f"process_schema: Handler for {step['parser']} yields metadata that are not a enclosed in a `dict`."
            if meta is not None:
                metadata.update(meta)
            assert (
                isinstance(comm, dict) or comm is None
            ), f"process_schema: Handler for {step['parser']} yields common data that are not enclosed in a `dict`."
            if comm is not None:
                common.update(comm)
        if common == dict():
            datagram["steps"].append({"metadata": metadata, "data": timesteps})
        else:
            datagram["steps"].append(
                {"metadata": metadata, "common": common, "data": timesteps}
            )
        if step.get("export", None) is not None:
            with open(step["export"], "w") as ofile:
                json.dump(datagram, ofile, indent=1)
    return datagram
