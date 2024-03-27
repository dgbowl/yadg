import json
from xarray import Dataset

from yadg.parsers.basiccsv.main import append_dicts, dicts_to_dataset
from yadg.parsers.electrochem.tomatojson import process


def dummy_tomato_json(*, fn: str, **kwargs: dict) -> Dataset:
    with open(fn, "r") as inf:
        jsdata = json.load(inf)

    data_vals = {}
    meta_vals = {}
    for vi, vals in enumerate(jsdata["data"]):
        vals["uts"] = vals.pop("time")
        devs = {}
        for k, v in vals.items():
            if k not in {"time", "address", "channel"}:
                devs[k] = 0.0
        append_dicts(vals, devs, data_vals, meta_vals, fn, vi)
    return dicts_to_dataset(data_vals, meta_vals, fulldate=False)


def extract(*, fn: str, **kwargs: dict) -> Dataset:

    with open(fn, "r") as inf:
        jsdata = json.load(inf)

    if "technique" in jsdata:
        return process(fn=fn, **kwargs)
    else:
        return dummy_tomato_json(fn=fn, **kwargs)


__all__ = ["extract"]
