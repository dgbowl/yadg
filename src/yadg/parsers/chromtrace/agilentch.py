"""
**agilentch**: Processing Agilent OpenLab binary signal trace files (CH and IT).
--------------------------------------------------------------------------------

Currently supports version "179" of the files. Version information is defined in
the `magic_values` (parameters & metadata) and `data_dtypes` (data) dictionaries.

Adapted from `ImportAgilent.m <https://bit.ly/3HSelIR>`_ and
`aston <https://github.com/bovee/Aston>`_.

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

.. codeauthor:: Peter Kraus
"""
import numpy as np
from zoneinfo import ZoneInfo
from ... import dgutils
from ...dgutils.dateutils import str_to_uts
import xarray as xr
from datatree import DataTree

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


def process(*, fn: str, timezone: ZoneInfo, **kwargs: dict) -> DataTree:
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
    class:`datatree.DataTree`
        A :class:`datatree.DataTree` containing one :class:`xarray.Dataset` per detector. As
        there is only one detector data in each CH file, this nesting is only for
        consistency with other filetypes.

    """

    with open(fn, "rb") as inf:
        ch = inf.read()

    magic = dgutils.read_value(ch, 0, "utf-8")
    pars = {}
    if magic in magic_values.keys():
        for offset, (tag, dtype) in magic_values[magic].items():
            v = dgutils.read_value(ch, offset, dtype)
            pars[tag] = v
    pars["end"] = len(ch)
    dsize, ddtype = data_dtypes[magic]
    pars["start"] = (pars["offset"] - 1) * 512
    nbytes = pars["end"] - pars["start"]
    assert nbytes % dsize == 0
    npoints = nbytes // dsize

    metadata = dict()
    for k in ["sampleid", "username", "method"]:
        metadata[k] = pars[k]
    metadata["version"] = str(magic)

    xsn = np.linspace(pars["xmin"] / 1000, pars["xmax"] / 1000, num=npoints)
    xss = np.ones(npoints) * xsn[0]
    ysn = (
        np.frombuffer(
            ch,
            offset=pars["start"],
            dtype=ddtype,
            count=npoints,
        )
        * pars["slope"]
    )
    yss = np.ones(npoints) * pars["slope"]

    detector, title = pars["tracetitle"].split(",")

    uts = str_to_uts(
        timestamp=pars["timestamp"], format="%d-%b-%y, %H:%M:%S", timezone=timezone
    )

    ds = xr.Dataset(
        data_vars={
            "signal": (
                ["uts", "elution_time"],
                [ysn],
                {"units": pars["yunit"], "ancillary_variables": "signal_std_err"},
            ),
            "signal_std_err": (
                ["uts", "elution_time"],
                [yss],
                {"units": pars["yunit"], "standard_name": "signal standard_error"},
            ),
            "elution_time_std_err": (
                ["elution_time"],
                xss,
                {"units": "s", "standard_name": "elution_time standard_error"},
            ),
        },
        coords={
            "elution_time": (
                ["elution_time"],
                xsn,
                {"units": "s", "ancillary_variables": "elution_time_std_err"},
            ),
            "uts": (["uts"], [uts]),
        },
        attrs={"title": title},
    )
    dt = DataTree.from_dict({detector: ds})
    dt.attrs = metadata
    return dt
