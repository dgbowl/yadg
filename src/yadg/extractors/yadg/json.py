"""
This module parses yadg ``json`` legacy datagrams.

Usage
`````
Available since ``yadg-7.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_7_0.filetype.Yadg_json

Schema
``````
.. code-block:: yaml

    xarray.DataTree:
      {{ step_name }}
        coords:
          uts:             !!float           # Unix timestamp, optional
        data_vars:
          {{ values }}:    (uts)             # Real part of the response


Uncertainties
`````````````
- all values: taken as explicit from previous yadg data.


.. codeauthor::
    Peter Kraus

"""

import json
import logging
from pathlib import Path
from xarray import Dataset, DataTree
from yadg.extractors import get_extract_dispatch


logger = logging.getLogger(__name__)
extract = get_extract_dispatch()


def process_ts(obj: list, data_vars: dict, units: dict):
    for ts in obj:
        if ts is None:
            continue
        for k, v in ts.items():
            k = sanitize_name(k)
            if isinstance(v, dict) and {"n", "s", "u"} == set(v.keys()):
                ku = f"{k.replace(' ', '_')}_uncertainty"
                if k not in data_vars:
                    data_vars[k] = []
                    data_vars[ku] = []
                    units[k] = []
                data_vars[k].append(v["n"])
                data_vars[ku].append(v["s"])
                units[k].append(v["u"])
            elif isinstance(v, dict):
                raise NotImplementedError(
                    "Recursive data has not been implemented yet."
                )
            else:
                if k not in data_vars:
                    data_vars[k] = []
                data_vars[k].append(v)


def build_attrs(key: str) -> dict:
    if key.endswith("_uncertainty"):
        k = key.replace("_uncertainty", "")
        attrs = {
            "standard_name": f"{k} standard_error",
            "standard_error_multiplier": 1,
            "yadg_uncertainty_type": "abs",
            "yadg_uncertainty_distribution": "rectangular",
            "yadg_uncertainty_source": "explicit",
        }
    else:
        ku = f"{key}_uncertainty"
        attrs = {"ancillary_variables": ku}
    return attrs


def sanitize_name(k: str) -> str:
    if k in {"ox/red", "CO/CO2"}:
        k = k.replace("/", " or ")
    return k


def vars_from_data(data: list[dict], ver: int) -> tuple[dict, dict, dict]:
    tmp = zip(data[0].keys(), *[[d.get(k) for k in data[0].keys()] for d in data])
    parts = {t[0]: t[1:] for t in tmp}

    meta = {}
    for k in {"fn"}:
        if k in parts:
            meta[k] = set(parts[k])

    coords = {
        "uts": (
            ["uts"],
            list(parts["uts"]),
        )
    }
    data_vars = {}
    units = {}
    if "raw" in parts:
        process_ts(obj=parts["raw"], data_vars=data_vars, units=units)
    if "derived" in parts:
        process_ts(obj=parts["derived"], data_vars=data_vars, units=units)

    if ver == 3:
        for k in parts:
            if isinstance(parts[k], (tuple,list)) and all([isinstance(p, float) for p in parts[k]]):
                data_vars[k]
            #if isinstance(parts[k][0], float):
            if k not in {"uts", "raw", "derived"}:
                print(f"{parts[k]=}")
                process_ts(obj=parts[k], data_vars=data_vars, units=units)

    for k in data_vars:
        if k.endswith("_uncertainty"):
            if len(set(data_vars[k])) == 1:
                data_vars[k] = ([], data_vars[k][0], build_attrs(k))
            else:
                data_vars[k] = (["uts"], data_vars[k], build_attrs(k))
        else:
            attrs = build_attrs(k)
            if k in units and len(set(units[k])) != 1:
                raise NotImplementedError("Inconsistent units not yet supported.")
            elif k in units:
                attrs.update({"units": units[k][0]})
            data_vars[k] = (["uts"], data_vars[k], attrs)

    return data_vars, coords, meta


def process_4_2(jsdata: dict) -> DataTree:
    dtdict = {}
    for step in jsdata["steps"]:
        tag = step["metadata"].pop("tag")
        data_vars, coords, meta = vars_from_data(step["data"], 4)
        attrs = dict(original_metadata=step["metadata"])
        attrs.update(meta)
        ds = Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
        dtdict[tag] = ds

    dt = DataTree.from_dict(dtdict)
    dt.attrs = dict(original_metadata=jsdata["metadata"])
    return dt

def process_3_x(jsdata: list) -> DataTree:
    dtdict = {}
    for step in jsdata:
        tag = step["input"]["export"]
        data_vars, coords, meta = vars_from_data(step["results"], 3)
        attrs = dict(original_metadata=step["metadata"])
        attrs.update(meta)
        ds = Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
        dtdict[tag] = ds

    dt = DataTree.from_dict(dtdict)
    #dt.attrs = dict(original_metadata=jsdata["metadata"])
    return dt



@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    encoding: str,
    **kwargs: dict,
) -> DataTree:
    with open(source, "r", encoding=encoding, errors="ignore") as infile:
        jsdata = json.load(infile)

    if isinstance(jsdata, list):
        return process_3_x(jsdata)
    elif jsdata["metadata"]["datagram_version"].startswith("4.2"):
        return process_4_2(jsdata)
