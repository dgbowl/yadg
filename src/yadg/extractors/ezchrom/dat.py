"""
Handles binary files created by EZChrom software.

Usage
`````
Available since ``yadg-5.1``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_6_0.filetype.EZChrom_dat

Schema
``````
.. code-block:: yaml

    xarray.DataTree:
      {{ detector_trace }}:
        coords:
          uts:            !!float               # Unix timestamp
          elution_time:   !!float               # Elution time
        data_vars:
          signal:         (uts, elution_time)   # Signal data

Uncertainties
`````````````
- ``signal``: using scaling from Y-axis multiplier.
- ``elution_time``: using scaling from X-axis multiplier.

Metadata
````````
No metadata is currently extracted. If you need some particular metadata, please open
an issue.

Notes on file structure
```````````````````````
Data in these files is stored as an OLE file, which is first processed using the
:mod:`olefile` library.

The timestamp is stored as an OLE timestamp in the ``Chrom Header`` stream.

The metadata for each trace are stored within the ``Detector Trace Handler`` stream,
and contain the X- and Y-axis multiplier, Y-axis units, and some other metadata.

The data for each trace are stored within the ``Detector Data`` "directory" within the
OLE file, with one stream per trace.


.. codeauthor::
    Peter Kraus

"""

import numpy as np
import olefile
from pathlib import Path
from xarray import DataTree, Dataset
from yadg import dgutils
from yadg.extractors import get_extract_dispatch

extract = get_extract_dispatch()


detector_trace_struct = [
    ("trace_name", 22, "pascal"),
    ("position", 4, "pascal"),
    ("x_mul", 0, "f4"),
    ("y_unit", 0, "pascal"),
    ("y_mul", 0, "f4"),
    ("tst", 33, "pascal"),
    ("y_unit2", 0, "pascal"),
    ("time", 21, "f4"),
]


@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    # Read data from the OLE file
    dd = {}
    with olefile.OleFileIO(source) as of:
        ch = of.openstream(["Chrom Header"]).read()
        dth = of.openstream(["Detector Trace Handler"]).read()
        for path in of.listdir():
            if len(path) == 2 and path[0] == "Detector Data":
                dd[path[1]] = of.openstream(path).read()
    # Timestamp
    ole_timestamp = dgutils.read_value(data=ch, offset=8, dtype="f8")
    uts = dgutils.ole_to_uts(ole_timestamp, timezone)

    # Trace metadata
    offset = 31
    dtp = {}
    for _ in dd:
        params = {}
        for name, delta, dtype in detector_trace_struct:
            offset += delta
            params[name] = dgutils.read_value(data=dth, offset=offset, dtype=dtype)
            if dtype == "pascal":
                offset += dgutils.read_value(data=dth, offset=offset, dtype="u1") + 1
            elif dtype == "f4":
                offset += 4
        dtp[f"Detector {params['trace_name']} Trace"] = params

    # Trace data
    dt = {}
    for key, vals in dd.items():
        par = dtp[key]
        npoints = dgutils.read_value(data=vals, offset=4, dtype="u4")
        yvals = np.frombuffer(vals, offset=20, count=npoints, dtype="i4") * par["y_mul"]
        xvals = np.arange(0, npoints) * par["x_mul"]

        ds = Dataset(
            data_vars={
                "signal": (
                    ["uts", "elution_time"],
                    [yvals],
                    {
                        "units": par["y_unit"].replace("25", "").strip(),
                        "ancillary_variables": "signal_uncertainty",
                    },
                ),
                "signal_uncertainty": (
                    [],
                    par["y_mul"],
                    {
                        "standard_name": "signal standard_error",
                        "standard_error_multiplier": 1,
                        "yadg_uncertainty_type": "abs",
                        "yadg_uncertainty_distribution": "rectangular",
                        "yadg_uncertainty_source": "scaling",
                    },
                ),
                "elution_time_uncertainty": (
                    [],
                    par["x_mul"],
                    {
                        "standard_name": "elution_time standard_error",
                        "standard_error_multiplier": 1,
                        "yadg_uncertainty_type": "abs",
                        "yadg_uncertainty_distribution": "rectangular",
                        "yadg_uncertainty_source": "scaling",
                    },
                ),
            },
            coords={
                "elution_time": (
                    ["elution_time"],
                    xvals,
                    {
                        "units": "s",
                        "ancillary_variables": "elution_time_uncertainty",
                    },
                ),
                "uts": (
                    ["uts"],
                    [uts],
                ),
            },
        )
        dt[f"/{key}"] = ds
    return DataTree.from_dict(dt)
