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

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_6_0.filetype.Agilent_csv

Schema
``````
.. code-block:: yaml

    xarray.DataTree:
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
from yadg.extractors import get_extract_dispatch
import xarray as xr
from pathlib import Path
from xarray import DataTree
import logging

logger = logging.getLogger(__name__)
extract = get_extract_dispatch()


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
    tvals, tdevs = [x for x in zip(*tx)]
    yvals, ydevs = [x for x in zip(*ty)]
    trace = {
        "tvals": np.array(tvals) * 60,
        "yvals": list(yvals),
        # CHROMTAB files seem to have fixed precision,
        # let us pick the maximum deviation and apply it
        "tdev": max(tdevs) * 60,
        "ydev": max(ydevs),
    }
    return trace


@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(source, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()
    orig_meta = {}
    uts = []
    tx = []
    ty = []
    detname = None
    tstep = dict()
    data = []
    traces = set()
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) > 2:
            if '"Date Acquired"' in parts:
                if tx != [] and ty != [] and detname is not None:
                    tstep[detname] = _to_trace(tx, ty)
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
                tstep[detname] = _to_trace(tx, ty)
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
    data.append(tstep)

    traces = sorted(traces)
    vals = {}
    for tr in traces:
        dsets = []
        for ti, ts in enumerate(data):
            ds = xr.Dataset(
                data_vars={
                    "signal": (
                        ["elution_time"],
                        ts[tr]["yvals"],
                        {"ancillary_variables": "signal_uncertainty"},
                    ),
                    "signal_uncertainty": (
                        [],
                        ts[tr]["ydev"],
                        {
                            "standard_name": "signal standard_error",
                            "yadg_uncertainty_absolute": 1,
                            "yadg_uncertainty_distribution": "rectangular",
                            "yadg_uncertainty_source": "sigfig",
                        },
                    ),
                    "elution_time_uncertainty": (
                        [],
                        ts[tr]["tdev"],
                        {
                            "units": "s",
                            "standard_name": "elution_time standard_error",
                            "yadg_uncertainty_absolute": 1,
                            "yadg_uncertainty_distribution": "rectangular",
                            "yadg_uncertainty_source": "sigfig",
                        },
                    ),
                },
                coords={
                    "elution_time": (
                        ["elution_time"],
                        ts[tr]["tvals"],
                        {
                            "units": "s",
                            "ancillary_variables": "elution_time_uncertainty",
                        },
                    ),
                    "uts": (["uts"], [uts[ti]]),
                },
                attrs={},
            )
            # ds["uts"] = [uts[ti]]
            dsets.append(ds)
        vals[tr] = xr.concat(
            dsets,
            dim="uts",
            data_vars="different",
            compat="identical",
            join="outer",
        )
    dt = DataTree.from_dict(vals)
    dt.attrs = {"original_metadata": orig_meta}
    return dt
