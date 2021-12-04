"""
File parser for the LabView CSV files generated using Agilent PNA-L N5320C.

This file format includes a header, with the values of bandwith and averaging,
and three tab-separated columns containing the frequency :math:`f`, and the real
and imaginary parts of the complex reflection coefficient :math:`\\Gamma(f)`.

Timestamps are determined from file name. One trace per file. As the set-up for
which this format was designed always uses the ``S11`` port, the name of the trace
is hard-coded to this value.

.. codeauthor:: Peter Kraus <peter.kraus@empa.ch>
"""

import os
import numpy as np
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

import yadg.dgutils


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

    # create timestamp
    _, datefunc = yadg.dgutils.infer_timestamp_from(
        timezone=timezone, spec={"timestamp": {"format": "%Y-%m-%d-%H-%M-%S"}}
    )
    dirname, basename = os.path.split(fn)
    data = {"uts": datefunc(os.path.splitext(basename)[0]), "fn": str(fn)}
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
    data["raw"] = {"traces": {}, "bw": {"n": bw[0], "s": bw[1], "u": "Hz"}, "avg": avg}
    freq = []
    gamma = []
    real = []
    imag = []
    absgamma = []
    for line in lines:
        f, re, im = line.strip().split()
        fn, fs = tuple_fromstr(f)
        fs = max(fs, fsbw)
        ren, res = tuple_fromstr(re)
        imn, ims = tuple_fromstr(im)
        freq.append([fn, fs])
        real.append([ren, res])
        imag.append([imn, ims])
        c = complex(ren, imn)
        gamma.append(c)
        absgamma.append(abs(c))
    temp = {"f": {}, "Re(Γ)": {}, "Im(Γ)": {}}
    freq = [np.array(i) for i in zip(*freq)]
    temp["fvals"], temp["fsigs"] = freq
    temp["gamma"] = np.array(gamma)
    temp["absgamma"] = np.array(absgamma)
    temp["f"]["n"], temp["f"]["s"] = [i.tolist() for i in freq]
    temp["f"]["u"] = "Hz"
    real = [np.array(i) for i in zip(*real)]
    temp["Re(Γ)"]["n"], temp["Re(Γ)"]["s"] = [i.tolist() for i in real]
    imag = [np.array(i) for i in zip(*imag)]
    temp["Im(Γ)"]["n"], temp["Im(Γ)"]["s"] = [i.tolist() for i in imag]
    data["raw"]["traces"]["S11"] = temp
    return [data], None
