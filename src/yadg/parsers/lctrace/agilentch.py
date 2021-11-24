import logging
import numpy as np
from uncertainties import ufloat_fromstr, ufloat, unumpy

import yadg.dgutils

magic_values = {}
magic_values["179"] = {
    0x035A: ("sampleid", "utf-16"),
    0x0559: ("description", "utf-16"),
    0x0A0E: ("method", "utf-16"),
    0x0758: ("username", "utf-16"),
    0x0957: ("timestamp", "utf-16"),
    0x09E5: ("instrument", "utf-16"),
    0x09BC: ("inlet", "utf-16"),
    0x104C: ("yunit", "utf-16"),
    0x1075: ("tracetitle", "utf-16"),
    0x0108: ("offset", ">i4"),  # (x-1) * 512
    0x011A: ("xmin", ">f4"),  # / 60000
    0x011E: ("xmax", ">f4"),  # / 60000
    0x1274: ("intercept", ">f8"),
    0x127C: ("slope", ">f8"),
}

data_dtypes = {}
data_dtypes["179"] = (8, "<f8")


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict, dict]:
    """
    Agilent OpenLAB signal trace parser

    One chromatogram per file with a single trace. A header section is followed by y-values for each trace. x-values have to be deduced using number of points, frequency, and x-multiplier. Method name is available, but detector names are not - they are assigned their numerical index in the file.
    """
    with open(fn, "rb") as infile:
        magic = yadg.dgutils.read_value(infile, 0, "utf-8", 1)

        pars = {}
        if magic in magic_values.keys():
            for offset, (tag, dtype) in magic_values[magic].items():
                v = yadg.dgutils.read_value(infile, offset, dtype, 1)
                pars[tag] = v
        pars["end"] = infile.seek(0, 2)
    dsize, ddtype = data_dtypes[magic]
    pars["start"] = (pars["offset"] - 1) * 512
    nbytes = pars["end"] - pars["start"]
    assert nbytes % dsize == 0
    npoints = nbytes // dsize

    xsn = np.linspace(pars["xmin"] / 1000, pars["xmax"] / 1000, num=npoints)
    xss = np.ones(npoints) * xsn[0]
    with open(fn, "rb") as infile:
        ysn = (
            yadg.dgutils.read_value(infile, pars["start"], ddtype, npoints)
            * pars["slope"]
        )
    yss = np.ones(npoints) * pars["slope"]

    detector, title = pars["tracetitle"].split(",")
    _, datefunc = yadg.dgutils.infer_timestamp_from(
        spec={"timestamp": {"format": "%d-%b-%y, %H:%M:%S"}}, timezone=timezone
    )

    chrom = {
        "fn": str(fn),
        "uts": datefunc(pars["timestamp"]),
        "traces": {
            detector: {
                "x": {"n": xsn.tolist(), "s": xss.tolist(), "u": "s"},
                "y": {"n": ysn.tolist(), "s": yss.tolist(), "u": pars["yunit"]},
                "id": 0,
                "data": [(xsn, xss), (ysn, yss)],
            }
        },
    }
    metadata = {"type": "lctrace.ch", "lcparams": {}}

    for k in ["sampleid", "username", "method"]:
        metadata["lcparams"][k] = pars[k]

    return [chrom], metadata, None
