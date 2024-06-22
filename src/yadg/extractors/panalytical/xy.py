"""
Handles processing of xy exports of Panalytical XRD files. When possible, the xrdml or
csv files should be used instead.

Usage
`````
Available since ``yadg-4.2``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Panalytical_xy

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      coords:
        angle:          !!float               # 2θ angle
      data_vars:
        intensity:      (angle)          # Measured intensity

Metadata
````````
No metadata is present in files.

Notes on file structure
```````````````````````

These files basically just contain the ``[Scan points]`` part of Panalytical csv files.
As a consequence, no metadata is recorded, and the format does not have an associated
timestamp.

.. codeauthor::
    Nicolas Vetsch,
    Peter Kraus
"""

from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import numpy as np
from datatree import DataTree
import xarray as xr


def extract(
    *,
    fn: str,
    encoding: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "r", encoding=encoding) as xy_file:
        xy = xy_file.readlines()
    datapoints = [li.strip().split() for li in xy]
    angle, intensity = list(zip(*datapoints))
    angle, _ = list(zip(*[tuple_fromstr(a) for a in angle]))
    insty, _ = list(zip(*[tuple_fromstr(i) for i in intensity]))
    idevs = np.ones(len(insty))
    adiff = np.abs(np.diff(angle)) * 0.5
    adiff = np.append(adiff, adiff[-1])
    vals = xr.Dataset(
        data_vars={
            "intensity": (
                ["angle"],
                list(insty),
                {"units": "counts", "ancillary_variables": "intensity_std_err"},
            ),
            "intensity_std_err": (
                ["angle"],
                idevs,
                {"units": "counts", "standard_name": "intensity standard_error"},
            ),
            "angle_std_err": (
                ["angle"],
                adiff,
                {"units": "deg", "standard_name": "angle standard_error"},
            ),
        },
        coords={
            "angle": (
                ["angle"],
                list(angle),
                {"units": "deg", "ancillary_variables": "angle_std_err"},
            ),
        },
    )
    return DataTree(vals)
