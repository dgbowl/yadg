"""
Used to process files generated using Agilent PNA-L N5320C via its LabVIEW driver.
This file format includes a header, with the values of bandwidth and averaging,
and three tab-separated columns containing the frequency :math:`f`, and the real
and imaginary parts of the complex reflection coefficient :math:`\\Gamma(f)`.

Note that no timestamps are present in the file and have to be supplied externally,
e.g. from the file name. One trace per file. As the MCPT set-up for which this
extractor was designed always uses the ``S11`` port, the node name is is hard-coded to
this value.

Usage
`````
Available since ``yadg-3.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.FHI_vna

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      S11:              !!xarray.Dataset
        coords:
            freq:       !!float     # An array of measurement frequencies
        data_vars:
            Re(G):      (freq)      # Real part of Γ
            Im(G):      (freq)      # Imaginary part of Γ
            average:    (None)      # Number of traces averaged
            bandwidth:  (None)      # Filter bandwidth

Metadata
````````
No metadata is returned.

.. codeauthor::
    Peter Kraus

"""

from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import xarray as xr
from datatree import DataTree


def extract(
    *,
    fn: str,
    encoding: str,
    **kwargs: dict,
) -> DataTree:
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
            "bandwidth": (
                [],
                bw[0],
                {"units": "Hz", "ancillary_variables": "bandwidth_std_err"},
            ),
            "bandwidth_std_err": (
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

    return DataTree.from_dict(dict(S11=vals))
