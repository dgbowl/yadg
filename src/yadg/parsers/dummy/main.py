from pydantic import BaseModel
import json
from zoneinfo import ZoneInfo
from ... import dgutils
from ..basiccsv.main import append_dicts, dicts_to_datasets
from datatree import DataTree


def process(
    *,
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
    locale: str,
    filetype: str,
    parameters: BaseModel,
) -> DataTree:
    """
    A dummy parser.

    This parser simply returns the current time, the filename provided, and any
    ``kwargs`` passed.

    In case the provided ``filetype`` is a ``tomato.json`` file, this is a json
    data file from the :mod:`tomato` package, which should contain a :class:`list`
    of ``{"value": float, "time": float}`` datapoints in its ``data`` entry.

    Parameters
    ----------
    fn
        Filename to process

    encoding
        Not used.

    timezone
        Not used

    parameters
        Parameters for :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.Dummy`.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. No metadata is
        returned by the dummy parser. The full date is always returned.

    """
    if filetype == "tomato.json":
        with open(fn, "r") as inf:
            jsdata = json.load(inf)

        data_vals = {}
        meta_vals = {"_fn": []}
        for vi, vals in enumerate(jsdata["data"]):
            devs = {k: 0.0 for k, v in vals.items() if k != "time"}
            vals["uts"] = vals.pop("time")
            append_dicts(vals, devs, data_vals, meta_vals, fn, vi)
    else:
        kwargs = {} if parameters is None else parameters.dict()
        if "parser" in kwargs:
            del kwargs["parser"]
        data_vals = {k: [v] for k, v in kwargs.items()}
        data_vals["uts"] = [dgutils.now()]
        meta_vals = {"_fn": [str(fn)]}

    return dicts_to_datasets(data_vals, meta_vals, fulldate=False)
