import json
import logging
import importlib
from typing import Callable
from datatree import DataTree

from dgbowl_schemas.yadg.dataschema import DataSchema
from yadg import dgutils

logger = logging.getLogger(__name__)


def infer_extractor(extractor: str) -> Callable:
    """
    A function that finds an :func:`extract` function of the supplied ``extractor``.

    """
    modname = f"yadg.extractors.{extractor}"
    try:
        m = importlib.import_module(modname)
        if hasattr(m, "extract"):
            return getattr(m, "extract")
    except ImportError:
        logger.critical(f"could not import module '{modname}'")
    raise RuntimeError


def process_schema(dataschema: DataSchema, strict_merge: bool = False) -> DataTree:
    """
    The main processing function of yadg.

    Takes in a :class:`DataSchema` object and returns a single :class:`DataTree` created
    from the :class:`DataSchema`.

    """
    if strict_merge:
        concatmode = "identical"
    else:
        concatmode = "drop_conflicts"

    while hasattr(dataschema, "update"):
        dataschema = dataschema.update()

    root = DataTree()
    root.attrs = {
        "yadg_provenance": "yadg process",
        "yadg_process_date": dgutils.now(asstr=True),
        "yadg_process_DataSchema": dataschema.model_dump_json(),
    }
    root.attrs.update(dgutils.get_yadg_metadata())

    for si, step in enumerate(dataschema.steps):
        logger.info(f"Processing step {si}.")

        # Backfill default timezone, locale, encoding.
        if step.extractor.timezone is None:
            step.extractor.timezone = dataschema.step_defaults.timezone

        if step.extractor.locale is None:
            step.extractor.locale = dataschema.step_defaults.locale
        if step.extractor.encoding is None:
            step.extractor.encoding = dataschema.step_defaults.encoding

        if step.tag is None:
            step.tag = f"{si}"

        handler = infer_extractor(step.extractor.filetype)
        todofiles = step.input.paths()
        vals = None
        if len(todofiles) == 0:
            logger.warning(f"No files processed by step '{step.tag}'.")
            vals = {}
        for tf in todofiles:
            logger.info(f"Processing file '{tf}'.")
            tasks = handler(fn=tf, **vars(step.extractor)).to_dict()
            fvals = {}
            for name, dset in tasks.items():
                if name == "/" and len(dset.variables) == 0:
                    # The root datatree node may sometimes carry metadata, even if
                    # there are no variables - we don't add 'uts' to those.
                    fvals[name] = dset
                else:
                    fvals[name] = dgutils.complete_uts(
                        dset, tf, step.externaldate, step.extractor.timezone
                    )
            vals = dgutils.merge_dicttrees(vals, fvals, concatmode)

        stepdt = DataTree.from_dict({} if vals is None else vals)
        stepdt.name = step.tag
        for k, v in stepdt.attrs.items():
            if isinstance(v, (dict, list)):
                stepdt.attrs[k] = json.dumps(v)
        extractor_model_json = step.extractor.model_dump_json(exclude_none=True)
        stepdt.attrs["yadg_extract_Extractor"] = extractor_model_json
        stepdt.parent = root
    return root
