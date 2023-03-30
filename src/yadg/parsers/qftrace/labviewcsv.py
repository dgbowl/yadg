"""
**labviewcsv**: Processing LabView CSV files generated using Agilent PNA-L N5320C.
----------------------------------------------------------------------------------

This file format includes a header, with the values of bandwith and averaging,
and three tab-separated columns containing the frequency :math:`f`, and the real
and imaginary parts of the complex reflection coefficient :math:`\\Gamma(f)`.

Timestamps are determined from file name. One trace per file. As the set-up for
which this format was designed always uses the ``S11`` port, the name of the trace
is hard-coded to this value.

.. codeauthor:: Peter Kraus <peter.kraus@empa.ch>
"""

import numpy as np
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import xarray as xr


def process(
    fn: str, encoding: str = "utf-8", timezone: str = "timezone"
) -> tuple[list, dict]:
    """
    VNA reflection trace parser.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    Returns
    -------
    (data, metadata) : tuple[list, None]
        Tuple containing the timesteps, metadata, and common data.
    """

    data = {"fn": str(fn)}
    with open(fn, "r", encoding=encoding) as infile:
        lines = infile.readlines()
    assert (
        len(lines) > 2
    ), f"qftrace: Only {len(lines)-1} points supplied in {fn}; fitting impossible."

    # process header
    bw = [10000.0, 1.0]
    avg = 15
    if ";" in lines[0]:
        items = lines.pop(0).split(";")
        for item in items:
            if item.startswith("BW"):
                bw = tuple_fromstr(item.split("=")[-1].strip())
            if item.startswith("AVG"):
                avg = int(item.split("=")[-1].strip())
    fsbw = bw[0] / avg

    # calculate precision of trace
    vals = {}
    devs = {}
    # data["raw"] = {"traces": {}, "bw": {"n": bw[0], "s": bw[1], "u": "Hz"}, "avg": avg}
    freq = {"vals": [], "devs": []}
    real = {"vals": [], "devs": []}
    imag = {"vals": [], "devs": []}
    for line in lines:
        f, re, im = line.strip().split()
        fn, fs = tuple_fromstr(f)
        fs = max(fs, fsbw)
        ren, res = tuple_fromstr(re)
        imn, ims = tuple_fromstr(im)
        freq["vals"].append(fn)
        freq["devs"].append(fs)
        real["vals"].append(ren)
        real["devs"].append(res)
        imag["vals"].append(imn)
        imag["devs"].append(ims)

    vals = xr.Dataset(
        data_vars={
            "Re(G)": (
                ["freq"],
                real["vals"],
                {"ancillary_variables": "Re(G)_std_err"},
            ),
            "Re(G)_std_err": (
                ["freq"],
                real["devs"],
                {"standard_name": "Re(G) standard_error"},
            ),
            "Im(G)": (
                ["freq"],
                imag["vals"],
                {"ancillary_variables": "Im(G)_std_err"},
            ),
            "Im(G)_std_err": (
                ["freq"],
                imag["devs"],
                {"standard_name": "Im(G) standard_error"},
            ),
            "average": avg,
            "bandwith": (
                [],
                bw[0],
                {"units": "Hz", "ancillary_variables": "bandwidth_std_err"},
            ),
            "bandwith_std_err": (
                [],
                bw[1],
                {"units": "Hz", "standard_name": "bandwidth standard_error"},
            ),
        },
        coords={
            "freq": (
                ["freq"],
                freq["vals"],
                {"units": "Hz", "ancillary_variables": "freq_std_err"},
            ),
            "freq_std_err": (
                ["freq"],
                freq["devs"],
                {"units": "Hz", "standard_name": "freq standard_error"},
            ),
        },
    )

    return vals
