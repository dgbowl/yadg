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

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_6_0.filetype.FHI_vna

Schema
``````
.. code-block:: yaml

    xarray.DataTree:
      coords:
        frequency:       !!float           # An array of measurement frequencies
      data_vars:
        S11_real:        (frequency)       # Real part of the response
        S11_imag:        (frequency)       # Imagunary part of the response
        average:         (None)            # Number of traces averaged
        bandwidth:       (None)            # Filter bandwidth

Uncertainties
`````````````
- ``frequency``: explicit from bandwidth / average
- all other values: string to float conversion


Metadata
````````
No metadata is returned.

.. codeauthor::
    Peter Kraus

"""

from pathlib import Path
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
from yadg.dgutils.table import process_table
from yadg.extractors import get_extract_dispatch
from xarray import DataTree, Dataset


extract = get_extract_dispatch()


@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    encoding: str,
    **kwargs: dict,
) -> DataTree:
    with open(source, "r", encoding=encoding) as infile:
        lines = infile.readlines()
    assert len(lines) > 2, (
        f"qftrace: Only {len(lines) - 1} points supplied in {source}; fitting impossible."
    )

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

    data_vars = process_table(
        lines=lines,
        headers=["frequency", "S11_real", "S11_imag"],
    )
    for k in {"S11_real", "S11_imag"}:
        data_vars[k] = (("frequency"), *data_vars[k][1:])

    data_vars["average"] = (
        [],
        avg,
    )
    data_vars["bandwidth"] = ([], bw[0], {"units": "Hz"})

    data_vars["frequency_uncertainty"] = (
        [],
        fsbw,
        {
            "standard_name": "frequency standard_error",
            "standard_error_multiplier": 1,
            "yadg_uncertainty_type": "abs",
            "yadg_uncertainty_distribution": "normal",
            "yadg_uncertainty_source": "explicit",
        },
    )

    coords = dict(frequency=data_vars.pop("frequency"))
    ds = Dataset(data_vars=data_vars, coords=coords)

    return DataTree(ds)
