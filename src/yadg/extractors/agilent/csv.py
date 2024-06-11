"""
Extractor of Agilent Chemstation Chromtab tabulated data files. This file format may
include multiple timesteps consisting of several traces each in a single CSV file. It
contains a header section for each timestep, followed by a detector name, and a sequence
of "X, Y" datapoints, which are stored as ``elution_time`` and ``signal``.

.. warning ::

    It is not guaranteed that the X-axis of the chromatogram (i.e. ``elution_time``) is
    consistent between the timesteps of the same trace. The traces are expanded to the
    length of the longest trace, and the shorter traces are padded with ``NaNs``.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Agilent_csv

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      {{ detector_name }}:
        coords:
          uts:            !!float               # Unix timestamp
          elution_time:   !!float               # Elution time
        data_vars:
          signal:         (uts, elution_time)   # Signal data

Metadata
````````
The following metadata is extracted:

    - ``sampleid``: Sample name.
    - ``datafile``: Original path of the data file.

Uncertainties
`````````````
All uncertainties are derived from the string representation of the floats.

.. codeauthor::
    Peter Kraus

"""

import numpy as np
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
from yadg import dgutils
import xarray as xr
from datatree import DataTree
import logging

logger = logging.getLogger(__name__)


def _process_headers(headers: list, columns: list, timezone: str) -> dict:
    orig_meta = {k: v.strip() for k, v in zip(headers, columns)}
    if "Date Acquired" in orig_meta:
        uts = dgutils.str_to_uts(
            timestamp=columns[headers.index("Date Acquired")].strip(),
            format="%d %b %Y %H:%M",
            timezone=timezone,
        )
    else:
        logger.warning("'Date Acquired' not in file header, cannot infer timestamp.")
        uts = None
    return orig_meta, uts


def _to_trace(tx, ty):
    tvals, tders = [x for x in zip(*tx)]
    yvals, yders = [x for x in zip(*ty)]
    trace = {
        "tvals": np.array(tvals) * 60,
        "tdevs": np.array(tders) * 60,
        "yvals": list(yvals),
        "ydevs": list(yders),
    }
    return trace


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()
    orig_meta = {}
    uts = []
    tx = []
    ty = []
    detname = None
    tstep = dict()
    data = []
    traces = set()
    maxlen = dict()
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) > 2:
            if '"Date Acquired"' in parts:
                if tx != [] and ty != [] and detname is not None:
                    trace = _to_trace(tx, ty)
                    tstep[detname] = trace
                    maxlen[detname] = max(maxlen.get(detname, 0), len(trace["tvals"]))
                    tx = []
                    ty = []
                if len(tstep) > 0:
                    data.append(tstep)
                    tstep = dict()
                headers = [p.replace('"', "") for p in parts]
            else:
                columns = [p.replace('"', "") for p in parts]
                ret = _process_headers(headers, columns, timezone)
                uts.append(ret[1])
                dgutils.merge_meta(orig_meta, ret[0])
        elif len(parts) == 1:
            if tx != [] and ty != [] and detname is not None:
                trace = _to_trace(tx, ty)
                tstep[detname] = trace
                maxlen[detname] = max(maxlen.get(detname, 0), len(trace["tvals"]))
                tx = []
                ty = []
            detname = parts[0].replace('"', "").split("\\")[-1]
            traces.add(detname)
        elif len(parts) == 2:
            x, y = [tuple_fromstr(i) for i in parts]
            tx.append(x)
            ty.append(y)
    trace = _to_trace(tx, ty)
    tstep[detname] = trace
    maxlen[detname] = max(maxlen.get(detname, 0), len(trace["tvals"]))
    data.append(tstep)

    traces = sorted(traces)
    vals = {}
    for tr in traces:
        dsets = []
        for ti, ts in enumerate(data):
            thislen = len(ts[tr]["tvals"])
            fvals = {}
            for k in {"yvals", "ydevs", "tvals", "tdevs"}:
                fvals[k] = np.ones(maxlen[tr]) * np.nan
                fvals[k][:thislen] = ts[tr][k]
            ds = xr.Dataset(
                data_vars={
                    "signal": (
                        ["elution_time"],
                        fvals["yvals"],
                        {"ancillary_variables": "signal_std_err"},
                    ),
                    "signal_std_err": (
                        ["elution_time"],
                        fvals["ydevs"],
                        {"standard_name": "signal standard_error"},
                    ),
                    "elution_time": (
                        ["_"],
                        fvals["tvals"],
                        {"units": "s", "ancillary_variables": "elution_time_std_err"},
                    ),
                    "elution_time_std_err": (
                        ["elution_time"],
                        fvals["tdevs"],
                        {"units": "s", "standard_name": "elution_time standard_error"},
                    ),
                },
                coords={},
                attrs={},
            )
            ds["uts"] = [uts[ti]]
            dsets.append(ds)
        vals[tr] = xr.concat(dsets, dim="uts")
    dt = DataTree.from_dict(vals)
    dt.attrs = {"original_metadata": orig_meta}
    return dt
