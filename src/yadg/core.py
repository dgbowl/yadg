from importlib import metadata
import logging
import importlib
import xarray as xr
import numpy as np
from typing import Callable
from zoneinfo import ZoneInfo
from datatree import DataTree
from xarray import Dataset
from pydantic import BaseModel

from dgbowl_schemas.yadg.dataschema import DataSchema
from yadg import dgutils

datagram_version = metadata.version("yadg")
logger = logging.getLogger(__name__)


def infer_extractor(extractor: str) -> Callable:
    """
    A function that finds an :func:`extract` function of the supplied ``extractor``.

    """
    modnames = [
        f"yadg.extractors.public.{extractor}",
        f"yadg.extractors.custom.{extractor}",
        f"yadg.extractors.{extractor.replace('.','')}"
    ]
    for modname in modnames:
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
        "provenance": "yadg process",
        "date": dgutils.now(asstr=True),
        "input_schema": dataschema.model_dump_json(),
        "datagram_version": datagram_version,
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

        sattrs = {"extractor_schema": step.extractor.model_dump_json(exclude_none=True)}
        step.extractor.timezone = ZoneInfo(step.extractor.timezone)

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
            ret = handler(fn=tf, **vars(step.extractor))
            if isinstance(ret, DataTree):
                tasks = ret.to_dict()
            elif isinstance(ret, Dataset):
                tasks = {"/": ret}
            else:
                raise RuntimeError(type(ret))
            fvals = {}
            for name, dset in tasks.items():
                if name == "/" and len(dset.variables) == 0:
                    # The root datatree node may sometimes carry metadata, even if
                    # there are no variables - we don't add 'uts' to those.
                    fvals[name] = dset
                else:
                    fvals[name] = complete_uts(
                        dset, tf, step.externaldate, step.extractor.timezone
                    )
            vals = merge_dicttrees(vals, fvals, concatmode)

        stepdt = DataTree.from_dict({} if vals is None else vals)
        stepdt.name = step.tag
        stepdt.attrs = sattrs
        stepdt.parent = root
    return root


def complete_uts(
    ds: Dataset,
    filename: str,
    externaldate: BaseModel,
    timezone: ZoneInfo,
) -> Dataset:
    """
    A helper function ensuring that the Dataset ``ds`` contains a dimension ``"uts"``,
    and that the timestamps in ``"uts"`` are completed as instructed in the
    ``externaldate`` specification.

    """
    if not hasattr(ds, "uts"):
        ds = ds.expand_dims("uts")
    if len(ds.uts.coords) == 0:
        ds["uts"] = np.zeros(ds.uts.size)
        ds.attrs["fulldate"] = False
    if not ds.attrs.get("fulldate", True) or externaldate is not None:
        ts, fulldate = dgutils.complete_timestamps(
            timesteps=ds.uts.values,
            fn=filename,
            spec=externaldate,
            timezone=timezone,
        )
        ds["uts"] = ts
        if fulldate:
            ds.attrs.pop("fulldate", None)
        else:
            # cannot store booleans in NetCDF files
            ds.attrs["fulldate"] = int(fulldate)

    return ds


def merge_dicttrees(vals: dict, fvals: dict, mode: str) -> dict:
    """
    A helper function that merges two ``DataTree.to_dict()`` objects by concatenating
    the new values in ``fvals`` to the existing ones in ``vals``.

    """
    if vals is None:
        return fvals
    for k in fvals.keys():
        try:
            vals[k] = xr.concat([vals[k], fvals[k]], dim="uts", combine_attrs=mode)
        except xr.MergeError:
            raise RuntimeError(
                "Merging metadata from multiple files has failed, as some of the "
                "values differ between files. This might be caused by trying to "
                "parse data obtained using different techniques/protocols in a "
                "single step. If you are certain this is what you want, try using "
                "yadg with the '--ignore-merge-errors' option."
            )
    return vals
