import json
import logging
import importlib
from typing import Callable
from .extractor import StepDefaults, Extractor
from dgbowl_schemas.yadg import DataSchema
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


def process_schema(dataschema: DataSchema) -> dict:
    """
    Main worker function of **yadg**.

    Takes in a :class:`DataSchema` object and returns a single annotated
    `datagram` created from the `dataschema`. It is the job of the user to supply a
    validated `schema`.

    Parameters
    ----------
    dataschema: DataSchema
        A fully validated `dataschema` object.

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

    while hasattr(dataschema, "update"):
        dataschema = dataschema.update()

    defaults = StepDefaults(dataschema.step_defaults)

    si = 0
    for step in dataschema.steps:
        logger.info("Processing step %d:", si)

        ex = Extractor(
            defaults, timezone=step.timezone, locale=step.locale, encoding=step.encoding
        )

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
                fn=tf,
                encoding=ex.encoding,
                timezone=ex.timezone,
                locale=ex.locale,
                filetype=step.filetype,
                parameters=step.parameters,
            )
            if not fulldate or step.externaldate is not None:
                dgutils.complete_timestamps(
                    timesteps=ts, fn=tf, spec=step.externaldate, timezone=ex.timezone
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
    return datagram
