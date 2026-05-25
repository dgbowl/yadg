"""
Handles processing of xy exports of Panalytical XRD files. When possible, the xrdml or
csv files should be used instead.

Usage
`````
Available since ``yadg-4.2``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_6_0.filetype.Panalytical_xy

Schema
``````
.. code-block:: yaml

    xarray.DataTree:
      coords:
        angle:          !!float               # 2θ angle
      data_vars:
        intensity:      (angle)          # Measured intensity

Uncertainties
`````````````
- all values: string to float conversion.

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

from pathlib import Path
from xarray import DataTree, Dataset
from yadg.dgutils.table import process_table
from yadg.extractors import get_extract_dispatch

extract = get_extract_dispatch()


@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    encoding: str,
    **kwargs: dict,
) -> DataTree:
    with open(source, "r", encoding=encoding) as xy_file:
        xy = xy_file.readlines()

    data_vars = process_table(
        lines=xy,
        headers=["angle", "intensity"],
    )
    data_vars["intensity"] = (
        ["angle"],
        data_vars["intensity"][1],
        data_vars["intensity"][2],
    )
    coords = dict(angle=data_vars.pop("angle"))
    ds = Dataset(data_vars=data_vars, coords=coords)
    return DataTree(ds)
