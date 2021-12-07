"""
File parser for Agilent OpenLab binary signal trace files (CH and IT).

Currently supports version "179" of the files. Version information is defined in
the `magic_values` (parameters & metadata) and `data_dtypes` (data) dictionaries.

Adapted from `ImportAgilent.m <https://bit.ly/3HSelIR>`_ and 
`aston <https://github.com/bovee/Aston>`_.

Exposed metadata:
`````````````````

.. code-block:: yaml

    params:
      method:   !!str
      sampleid: !!str
      username: !!str
      version:  !!str
      valve:    None
      datafile: None

File Structure of ``.ch`` files
```````````````````````````````
.. code ::

    0x0000 "version magic"
    0x0108 "data offset"
    0x011a "x-axis minimum (ms)"
    0x011e "x-axis maximum (ms)"
    0x035a "sample ID"
    0x0559 "description"
    0x0758 "username"
    0x0957 "timestamp"
    0x09e5 "instrument name"
    0x09bc "inlet"
    0x0a0e "method"
    0x104c "y-axis unit"
    0x1075 "detector name"
    0x1274 "y-axis intercept"
    0x127c "y-axis slope"

Data is stored in a consecutive set of ``<f8``, starting at the offset (calculated
as ``offset =  ("data offset" - 1) * 512``) until the end of the file.

.. codeauthor:: Peter Kraus <peter.kraus@empa.ch>
"""
import numpy as np

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


def process(fn: str, encoding: str, timezone: str) -> tuple[list, dict]:
    """
    Agilent OpenLAB signal trace parser

    One chromatogram per file with a single trace. Binary data format.

    Parameters
    ----------
    fn
        Filename to process.

    encoding
        Not used as the file is binary.

    timezone
        Timezone information. This should be ``"localtime"``.

    Returns
    -------
    ([chrom], metadata): tuple[list, dict]
        Standard timesteps & metadata tuple.
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
                "t": {"n": xsn.tolist(), "s": xss.tolist(), "u": "s"},
                "y": {"n": ysn.tolist(), "s": yss.tolist(), "u": pars["yunit"]},
                "id": 0,
                "data": [(xsn, xss), (ysn, yss)],
            }
        },
    }
    metadata = {"type": "agilent.ch", "params": {}}

    for k in ["sampleid", "username", "method"]:
        metadata["params"][k] = pars[k]
    metadata["params"]["valve"] = None
    metadata["params"]["version"] = str(magic)
    metadata["params"]["datafile"] = None

    return [chrom], metadata
