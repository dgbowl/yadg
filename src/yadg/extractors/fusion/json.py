"""
For processing Inficon Fusion json data.  Contains both the data from the raw
chromatogram and the post-processed results.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Fusion_json

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      coords:
        uts:              !!float
        species:          !!str
      data_vars:
        height:           (uts, species)        # Peak height at maximum
        area:             (uts, species)        # Integrated peak area
        concentration:    (uts, species)        # Calibrated peak area
        xout:             (uts, species)        # Mole fraction (normalized conc.)
        retention time:   (uts, species)        # Peak retention time
      {{ detector_name }}:
        coords:
          uts:            !!float               # Unix timestamp
          elution_time:   !!float               # Elution time
        data_vars:
          signal:         (uts, elution_time)   # Signal data
          valve:          (uts)                 # Valve position

Metadata
````````
No metadata is currently extracted.

.. codeauthor::
    Peter Kraus

"""

import json
import logging
from datatree import DataTree
from xarray import Dataset
import xarray as xr
import numpy as np

from yadg import dgutils


logger = logging.getLogger(__name__)


def chromdata(jsdata: dict, uts: float) -> Dataset:
    metadata = {
        "method": jsdata.get("methodName", "n/a"),
        "version": jsdata.get("softwareVersion", {}).get("version", None),
        "datafile": jsdata.get("sequence", {}).get("location", None),
    }

    sampleid = jsdata.get("annotations", {}).get("name", None)
    if sampleid is not None:
        metadata["sampleid"] = sampleid

    units = {
        "height": None,
        "area": None,
        "concentration": "%",
        "xout": "%",
        "retention time": "s",
    }

    raw = {
        "height": {},
        "area": {},
        "concentration": {},
        "xout": {},
        "retention time": {},
    }

    species = set()

    # sort detector keys to ensure alphabetic order for ID matching
    for detname in sorted(jsdata["detectors"].keys()):
        detdict = jsdata["detectors"][detname]
        if "analysis" in detdict:
            for peak in detdict["analysis"]["peaks"]:
                if "label" not in peak:
                    continue
                else:
                    species.add(peak["label"])
                if "height" in peak:
                    raw["height"][peak["label"]] = (float(peak["height"]), 1.0)
                if "area" in peak:
                    raw["area"][peak["label"]] = (float(peak["area"]), 0.01)
                if "concentration" in peak:
                    raw["concentration"][peak["label"]] = (
                        float(peak["concentration"]),
                        float(peak["concentration"]) * 1e-3,
                    )
                if "normalizedConcentration" in peak:
                    raw["xout"][peak["label"]] = (
                        float(peak["normalizedConcentration"]),
                        float(peak["normalizedConcentration"]) * 1e-3,
                    )
                if "top" in peak:
                    raw["retention time"][peak["label"]] = (float(peak["top"]), 0.01)

    valve = jsdata.get("annotations", {}).get("valcoPosition", None)
    if valve is not None:
        raw["valve"] = valve

    species = sorted(species)
    data_vars = {}
    for k, v in units.items():
        vals, devs = zip(*[raw[k].get(s, (np.nan, np.nan)) for s in species])
        data_vars[k] = (
            ["uts", "species"],
            [vals],
            {"ancillary_variables": f"{k}_std_err"},
        )
        data_vars[f"{k}_std_err"] = (
            ["uts", "species"],
            [devs],
            {"standard_name": f"{k} stdandard_error"},
        )
        if v is not None:
            data_vars[k][2]["units"] = v
            data_vars[f"{k}_std_err"][2]["units"] = v

    ds = xr.Dataset(
        data_vars=data_vars,
        coords={"species": (["species"], species), "uts": (["uts"], [uts])},
        attrs=dict(original_metadata=metadata),
    )
    return ds


def chromtrace(jsdata: dict, uts: float) -> DataTree:
    metadata = {
        "method": jsdata.get("methodName", "n/a"),
        "sampleid": jsdata.get("annotations", {}).get("name", None),
        "version": jsdata.get("softwareVersion", {}).get("version", None),
        "datafile": jsdata.get("sequence", {}).get("location", None),
    }

    # sort detector keys to ensure alphabetic order for ID matching
    traces = sorted(jsdata["detectors"].keys())
    vals = {}
    for detname in traces:
        detdict = jsdata["detectors"][detname]
        fvals = xr.Dataset(
            data_vars={
                "signal": (
                    ["uts", "elution_time"],
                    [detdict["values"]],
                    {"ancillary_variables": "signal_std_err"},
                ),
                "signal_std_err": (
                    ["uts", "elution_time"],
                    [np.ones(detdict["nValuesExpected"])],
                    {"standard_name": "signal standard_error"},
                ),
                "elution_time_std_err": (
                    ["elution_time"],
                    np.ones(detdict["nValuesExpected"]) / detdict["nValuesPerSecond"],
                    {"units": "s", "standard_name": "elution_time standard_error"},
                ),
            },
            coords={
                "elution_time": (
                    ["elution_time"],
                    np.arange(detdict["nValuesExpected"]) / detdict["nValuesPerSecond"],
                    {"units": "s", "ancillary_variables": "elution_time_std_err"},
                ),
                "uts": (["uts"], [uts]),
            },
            attrs={},
        )
        valve = jsdata.get("annotations", {}).get("valcoPosition", None)
        if valve is not None:
            fvals["valve"] = valve
        vals[detname] = fvals

    dt = DataTree.from_dict(vals)
    dt.attrs = dict(original_metadata=metadata)
    return dt


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        jsdata = json.load(infile)
    uts = dgutils.str_to_uts(timestamp=jsdata["runTimeStamp"], timezone=timezone)
    data = chromdata(jsdata, uts)
    trace = chromtrace(jsdata, uts)
    newdt = DataTree(data)
    for k, v in trace.items():
        newdt[k] = v
    return newdt
