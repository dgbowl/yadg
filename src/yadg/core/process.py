import json
import logging
import importlib
from typing import Callable
from packaging import version
from dgbowl_schemas.yadg import latest_version, DataSchema_4_0
from .. import dgutils, core

logger = logging.getLogger(__name__)


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
    modname = f"yadg.parsers.{parser}"
    try:
        m = importlib.import_module(modname)
        func = getattr(m, "process")
        return func
    except ImportError as e:
        logger.critical(f"could not import module '{modname}'")
        raise e


def process_schema(dataschema) -> dict:
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
            "provenance": {
                "yadg": dgutils.get_yadg_metadata(),
            },
            "date": dgutils.now(asstr=True),
            "input_schema": dataschema.dict(),
            "datagram_version": core.spec_datagram.datagram_version,
        },
        "steps": [],
    }

    current_version = dataschema.metadata.version
    if version.parse(current_version) < version.parse(latest_version):
        logger.warning(
            "The version of the provided DataSchema '%s' is older than the current "
            "latest version of DataSchema '%s'. Consider updating your schema.",
            current_version,
            latest_version,
        )

    si = 0
    for step in dataschema.steps:
        logger.info("Processing step %d:", si)
        metadata = dict()
        timesteps = list()
        handler = _infer_datagram_handler(step.parser)
        metadata["tag"] = f"{si:02d}" if step.tag is None else step.tag
        metadata["parser"] = step.parser
        todofiles = step.input.paths()
        if len(todofiles) == 0:
            logger.warning("No files processed by step '%s'.", metadata["tag"])
        for tf in todofiles:
            logger.info("Processing file '%s'.", tf)
            ts, meta, fulldate = handler(
                tf,
                encoding=step.input.encoding,
                timezone=dataschema.metadata.timezone,
                parameters=step.parameters,
            )
            if not fulldate or step.externaldate is not None:
                dgutils.complete_timestamps(
                    ts, tf, step.externaldate, dataschema.metadata.timezone
                )
            assert isinstance(ts, list), (
                f"Handler for '{step.parser}' yields timesteps "
                "that are not a enclosed in a 'list'."
            )
            timesteps += ts
            assert isinstance(meta, dict) or meta is None, (
                f"Handler for '{step.parser}' yields metadata "
                "that are not a enclosed in a 'dict'."
            )
            if meta is not None:
                metadata.update(meta)

        datagram["steps"].append({"metadata": metadata, "data": timesteps})
        if isinstance(dataschema, DataSchema_4_0):
            if step.export is not None:
                with open(step["export"], "w") as ofile:
                    json.dump(datagram, ofile, indent=1)
    return datagram
