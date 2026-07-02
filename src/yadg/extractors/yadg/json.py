"""
This module can be used to update yadg ``json`` legacy datagrams.

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
          uts:             !!float           # Unix timestamp
        data_vars:
          {{ values }}:    (uts)             # Data present in source datagram


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


def ziplist(obj: list) -> dict:
    okeys = obj[0].keys()
    tmp = zip(okeys, *[[d.get(k) for k in okeys] for d in obj])
    return {t[0]: t[1:] for t in tmp}


def store_nsu(key: str, parts: dict, data_vars: dict, dims: list):
    assert len(set(parts["u"])) == 1
    attrs = build_attrs(key)
    if parts["u"][0] is not None:
        attrs["units"] = parts["u"][0]
    data_vars[key] = ([d for d in dims], list(parts["n"]), attrs)

    ku = f"{key.replace(' ', '_')}_uncertainty"
    attrs = build_attrs(ku)
    if parts["u"][0] is not None:
        attrs["units"] = parts["u"][0]

    if "uts" in dims and all([ts == parts["s"][0] for ts in parts["s"]]):
        dims.pop(dims.index("uts"))
        data_vars[ku] = ([d for d in dims], parts["s"][0], attrs)
    else:
        data_vars[ku] = ([d for d in dims], list(parts["s"]), attrs)


def process_ts(obj: list, data_vars: dict, coords: dict):
    parts = ziplist(obj)
    for k, v in parts.items():
        k = sanitize_name(k)
        if all([isinstance(ts, dict) for ts in v]):
            vparts = ziplist(v)
            if {"n", "s", "u"} == set(vparts.keys()):
                store_nsu(k, vparts, data_vars, ["uts"])
            elif k == "traces":
                for kk in vparts:
                    vvparts = ziplist(vparts[kk])
                    if kk == "S11":
                        fparts = ziplist(vvparts["f"])
                        dim = "frequency"
                        assert all([ts == fparts["n"][0] for ts in fparts["n"]])
                        fparts["n"] = fparts["n"][0]
                        fparts["s"] = fparts["s"][0]
                        store_nsu(dim, fparts, data_vars, [dim])
                        for name in {"Re(G)", "Re(Γ)", "Im(G)", "Im(Γ)"}:
                            if name.startswith("Re"):
                                tag = f"{kk}_real"
                            else:
                                tag = f"{kk}_imag"
                            if name in vvparts:
                                vvvparts = ziplist(vvparts[name])
                                store_nsu(tag, vvvparts, data_vars, ["uts", dim])
                    elif {"id", "t", "y"} == set(vvparts.keys()):
                        tparts = ziplist(vvparts["t"])
                        dim = f"elution_time({kk})"
                        assert all([ts == tparts["n"][0] for ts in tparts["n"]])
                        tparts["n"] = tparts["n"][0]
                        tparts["s"] = tparts["s"][0]
                        store_nsu(dim, tparts, data_vars, [dim])
                        yparts = ziplist(vvparts["y"])
                        store_nsu(f"signal({kk})", yparts, data_vars, ["uts", dim])
                    else:
                        raise NotImplementedError(
                            f"Processing of trace {kk!r} not yet implemented."
                        )
            elif k == "S11":
                for name in {"Q", "f"}:
                    vvparts = ziplist(vparts[name])
                    store_nsu(f"{k}_{name}", vvparts, data_vars, ["uts", k])
            else:
                raise NotImplementedError(
                    "Recursive data has not been implemented yet."
                )
        else:
            data_vars[k] = (["uts"], list(v))


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


def vars_from_4_x_data(data: list[dict]) -> tuple[dict, dict, dict]:
    tmp = zip(data[0].keys(), *[[d.get(k) for k in data[0].keys()] for d in data])
    parts = {t[0]: t[1:] for t in tmp}

    meta = {}
    for k in {"fn"}:
        if k in parts:
            meta[k] = list(set(parts[k]))

    coords = {
        "uts": (
            ["uts"],
            list(parts["uts"]),
        )
    }
    data_vars = {}
    if "raw" in parts:
        process_ts(obj=parts["raw"], data_vars=data_vars, coords=coords)
    if "derived" in parts:
        process_ts(obj=parts["derived"], data_vars=data_vars, coords=coords)

    return data_vars, coords, meta


def process_4_x(jsdata: dict) -> DataTree:
    dtdict = {}
    for step in jsdata["steps"]:
        tag = step["metadata"].pop("tag")
        data_vars, coords, meta = vars_from_4_x_data(step["data"])
        attrs = dict(original_metadata=step["metadata"])
        # We do not store the fn key for now.
        # attrs.update(meta)
        ds = Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
        if tag in dtdict:
            logger.warning(f"Duplicate tag {tag!r} in datagram.")
            tag = f"{len(dtdict.keys()):02d}"
        dtdict[tag] = ds

    dt = DataTree.from_dict(dtdict)
    dt.attrs = dict(original_metadata=jsdata["metadata"])
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
        raise NotImplementedError(
            "Upgrading datagrams from version 3.1.0 is not supported. "
            "If you need this functionality, please file a bug report."
        )
    elif jsdata["metadata"]["datagram_version"].startswith("4.0"):
        return process_4_x(jsdata)
    elif jsdata["metadata"]["datagram_version"].startswith("4.1"):
        return process_4_x(jsdata)
    elif jsdata["metadata"]["datagram_version"].startswith("4.2"):
        return process_4_x(jsdata)
