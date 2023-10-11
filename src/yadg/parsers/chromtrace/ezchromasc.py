"""
**ezchromasc**: Processing EZ-Chrom ASCII export files (dat.asc).
-----------------------------------------------------------------

This file format includes one timestep with multiple traces in each ASCII file. It
contains a header section, and a sequence of Y datapoints (``signal``) for each detector.
The X-axis (``elution_time``) is assumed to be uniform between traces, and its units have
to be deduced from the header.

.. codeauthor:: Peter Kraus
"""
import numpy as np
import logging
from zoneinfo import ZoneInfo
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
from ...dgutils.dateutils import str_to_uts
import xarray as xr
from datatree import DataTree

logger = logging.getLogger(__name__)


def process(*, fn: str, encoding: str, timezone: ZoneInfo, **kwargs: dict) -> DataTree:
    """
    EZ-Chrome ASCII export file parser.

    One chromatogram per file with multiple traces. A header section is followed by
    y-values for each trace. x-values have to be deduced using number of points,
    frequency, and x-multiplier. Method name is available, but detector names are not.
    They are assigned their numerical index in the file.

    Parameters
    ----------
    fn
        Filename to process.

    encoding
        Encoding used to open the file.

    timezone
        Timezone information. This should be ``"localtime"``.


    Returns
    -------
    class:`datatree.DataTree`
        A :class:`datatree.DataTree` containing one :class:`xarray.Dataset` per detector.

    """

    with open(fn, "r", encoding=encoding, errors="ignore") as infile:
        lines = infile.readlines()
    metadata = {}
    data = {}

    for line in lines:
        for key in ["Version", "Method", "User Name"]:
            if line.startswith(key):
                k = key.lower().replace(" ", "")
                metadata[k] = line.split(f"{key}:")[1].strip()
        for key in ["Sample ID"]:  # , "Data File"]:
            if line.startswith(key):
                k = key.lower().replace(" ", "")
                metadata[k] = line.split(f"{key}:")[1].strip()
        if line.startswith("Acquisition Date and Time:"):
            uts = str_to_uts(
                timestamp=line.split("Time:")[1].strip(),
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
            yunits = [each.strip() for each in parts[1:]]
            if "25 V" in yunits:
                logger.warning("Implicit conversion of y-axis unit from '25 V' to 'V'.")
                yunits = [i.replace("25 V", "V") for i in yunits]
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
    dt.attrs = metadata
    return dt
