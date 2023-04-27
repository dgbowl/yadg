import logging
import importlib
from typing import Callable
from zoneinfo import ZoneInfo
from dgbowl_schemas.yadg import DataSchema
from datatree import DataTree
import xarray as xr
import numpy as np
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


def process_schema(dataschema: DataSchema) -> DataTree:
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
    datagram: DataTree
        An unvalidated `datagram`. The `parser`\\ s included in **yadg** should return
        a valid `datagram`; any custom `parser`\\ s might not do so. Use the function
        :meth:`yadg.core.validators.validate_datagram` to validate the resulting `datagram`.
    """

    root = DataTree()
    root.attrs = {
        "provenance": "yadg",
        "date": dgutils.now(asstr=True),
        "input_schema": dataschema.json(),
        "datagram_version": core.spec_datagram.datagram_version,
    }
    root.attrs.update(dgutils.get_yadg_metadata())

    while hasattr(dataschema, "update"):
        dataschema = dataschema.update()

    for si, step in enumerate(dataschema.steps):
        logger.info("Processing step %d:", si)

        # Backfill default timezone, locale, encoding.
        if step.extractor.timezone is None:
            tz = ZoneInfo(dataschema.step_defaults.timezone)
        else:
            tz = ZoneInfo(step.extractor.timezone)
        if step.extractor.locale is None:
            loc = dataschema.step_defaults.locale
        else:
            loc = step.extractor.locale
        if step.extractor.encoding is None:
            enc = dataschema.step_defaults.encoding
        else:
            enc = step.extractor.encoding

        if step.tag is None:
            step.tag = f"{si}"

        handler = _infer_datagram_handler(step.parser)
        todofiles = step.input.paths()
        if len(todofiles) == 0:
            logger.warning("No files processed by step '%s'.", step.tag)
        vals = None
        for tf in todofiles:
            logger.info("Processing file '%s'.", tf)
            fvals = handler(
                fn=tf,
                encoding=enc,
                timezone=tz,
                locale=loc,
                filetype=step.extractor.filetype,
                parameters=step.parameters,
            )
            if isinstance(fvals, DataTree):
                tasks = [(k, v.to_dataset()) for k, v in fvals.items()]
            else:
                tasks = [(None, fvals)]
            for task in tasks:
                name, dset = task
                for k in dset:
                    assert (
                        "/" not in k
                    ), f"The character '/' cannot be used in variable names: '{k}'."
                if not hasattr(dset, "uts"):
                    dset = dset.expand_dims("uts")
                if len(dset.uts.coords) == 0:
                    dset["uts"] = np.zeros(dset.uts.size)
                    dset.attrs["fulldate"] = False
                if (
                    not dset.attrs.get("fulldate", True)
                    or step.externaldate is not None
                ):
                    ts, fulldate = dgutils.complete_timestamps(
                        timesteps=dset.uts.values,
                        fn=tf,
                        spec=step.externaldate,
                        timezone=tz,
                    )
                    dset["uts"] = ts
                    if fulldate:
                        dset.attrs.pop("fulldate", None)
                    else:
                        dset.attrs["fulldate"] = fulldate
                if name is None:
                    fvals = dset
                else:
                    fvals[name] = DataTree(dset)
            if vals is None:
                vals = fvals
            elif isinstance(vals, xr.Dataset):
                vals = xr.concat([vals, fvals], dim="uts", combine_attrs="identical")
            elif isinstance(vals, DataTree):
                for k, v in fvals.items():
                    if k in vals: # pylint: disable=E1135
                        newv = xr.concat(
                            [vals[k].ds, v.ds], dim="uts", combine_attrs="identical"
                        ) # pylint: disable=E1136
                    else:
                        newv = v.ds
                    vals[k] = DataTree(newv) # pylint: disable=E1137
        if isinstance(vals, xr.Dataset):
            stepdt = DataTree.from_dict({"/": vals})
        elif isinstance(vals, DataTree):
            stepdt = vals
        else:
            stepdt = DataTree()
        stepdt.name = step.tag
        stepdt.attrs = dict(parser=step.parser)
        stepdt.parent = root
    return root
