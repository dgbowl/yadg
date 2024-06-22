"""
Handles files created using the ASCII export function in the EZChrom software.
This file format includes one timestep with multiple traces for each ASCII file. It
contains a header section, and a sequence of Y datapoints (``signal``) for each
detector. The X-axis (``elution_time``) is assumed to be uniform between traces, and
its units have to be deduced from the header.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.EZChrom_asc

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      {{ detector_index }}:
        coords:
          uts:            !!float               # Unix timestamp
          elution_time:   !!float               # Elution time
        data_vars:
          signal:         (uts, elution_time)   # Signal data

Metadata
````````
The following metadata is extracted:

    - ``sampleid``: Sample name.
    - ``username``: User name used to generate the file.
    - ``method``: Name of the chromatographic method.
    - ``version``: Version of the CH file (only "179" is currently supported.)

Uncertainties
`````````````
The uncertainties in ``signal`` are derived from the string representation of the float.

For ``elution_time``, an uncertainty of one X-axis multiplier is used.


.. codeauthor::
    Peter Kraus

"""

import numpy as np
import logging
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import xarray as xr
from datatree import DataTree

from yadg import dgutils

logger = logging.getLogger(__name__)


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()
    metadata = {}
    data = {}

    for line in lines:
        for key in ["Version", "Method", "User Name"]:
            if line.startswith(key):
                k = key.lower().replace(" ", "")
                metadata[k] = line.split(f"{key}:")[1].strip().strip(",")
        for key in ["Sample ID"]:  # , "Data File"]:
            if line.startswith(key):
                k = key.lower().replace(" ", "")
                metadata[k] = line.split(f"{key}:")[1].strip().strip(",")
        if line.startswith("Acquisition Date and Time:"):
            uts = dgutils.str_to_uts(
                timestamp=line.split("Time:")[1].strip().strip(","),
                format="%m/%d/%Y %I:%M:%S %p",
                timezone=timezone,
            )
        if line.startswith("Sampling Rate:"):
            assert (
                "Hz" in line
            ), f"datasc: Incorrect units for rate in file {fn}: {line}"
            parts = line.split("\t")
            samplerates = [float(each.strip()) for each in parts[1:-1]]
        if line.startswith("Total Data Points:"):
            assert (
                "Pts." in line
            ), f"datasc: Incorrect units for number of points in file {fn}: {line}"
            parts = line.split("\t")
            npoints = [int(each.strip()) for each in parts[1:-1]]
        if line.startswith("X Axis Title:"):
            parts = line.split("\t")
            xunits = [each.strip() for each in parts[1:]]
        if line.startswith("Y Axis Title:"):
            parts = line.split("\t")
            _yunits = [each.strip() for each in parts[1:]]
            yunits = [i.replace("25", "").strip() for i in _yunits]
            if yunits != _yunits:
                logger.warning(
                    "Implicit conversion of y-axis unit from '25 µV' to 'µV'."
                )
                yunits = [i.replace("25", "") for i in yunits]
        if line.startswith("X Axis Multiplier:"):
            parts = line.split("\t")
            xmuls = [float(each.strip()) for each in parts[1:]]
        if line.startswith("Y Axis Multiplier:"):
            parts = line.split("\t")
            ymuls = [float(each.strip()) for each in parts[1:]]
        if ":" not in line:
            si = lines.index(line)
            break
    assert (
        len(samplerates)
        == len(npoints)
        == len(xunits)
        == len(yunits)
        == len(xmuls)
        == len(ymuls)
    ), f"datasc: Inconsistent number of traces in {fn}."

    data = {}
    units = {}
    for ti, npts in enumerate(npoints):
        assert (
            xunits[ti] == "Minutes"
        ), f"datasc: X units label of trace {ti} in {fn} was not understood."
        dt = 60
        xmul = xmuls[ti] * dt / samplerates[ti]
        ymul = ymuls[ti]
        xsn = np.arange(npts) * xmul
        xss = np.ones(npts) * xmul
        ysn, yss = zip(*[tuple_fromstr(li) for li in lines[si : si + npts]])
        si += npts
        data[f"{ti}"] = {
            "t": (xsn, xss),
            "y": (np.array(ysn) * ymul, np.array(yss) * ymul),
        }
        units[f"{ti}"] = {"t": "s", "y": yunits[ti]}

    traces = sorted(data.keys())
    vals = {}
    for ti in traces:
        fvals = xr.Dataset(
            data_vars={
                "signal": (
                    ["uts", "elution_time"],
                    [data[ti]["y"][0]],
                    {"units": units[ti]["y"], "ancillary_variables": "signal_std_err"},
                ),
                "signal_std_err": (
                    ["uts", "elution_time"],
                    [data[ti]["y"][1]],
                    {"units": units[ti]["y"], "standard_name": "signal standard_error"},
                ),
                "elution_time_std_err": (
                    ["elution_time"],
                    data[ti]["t"][1],
                    {
                        "units": units[ti]["t"],
                        "standard_name": "elution_time standard_error",
                    },
                ),
            },
            coords={
                "elution_time": (
                    ["elution_time"],
                    data[ti]["t"][0],
                    {
                        "units": units[ti]["t"],
                        "ancillary_variables": "elution_time_std_err",
                    },
                ),
                "uts": (["uts"], [uts]),
            },
            attrs={},
        )
        vals[ti] = fvals
    dt = DataTree.from_dict(vals)
    dt.attrs = dict(original_metadata=metadata)
    return dt
