"""
Handles processing of csv exports of Panalytical XRD files.

Usage
`````
Available since ``yadg-4.2``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_6_0.filetype.Panalytical_csv

Schema
``````
.. code-block:: yaml

    xarray.DataTree:
      coords:
        uts:            !!float               # Unix timestamp
        angle:          !!float               # 2θ angle
      data_vars:
        intensity:      (uts, angle)          # Measured intensity

Uncertainties
`````````````
- ``angle``: string to float conversion.
- ``intensity``: string to float conversion.

Metadata
````````
With the exception of the ``comment``, the metadata present in the csv file is extracted
from the file header without post-processing.

Notes on file structure
```````````````````````
These files are split into a ``[Measurement conditions]`` and a ``[Scan points]``
section. The former stores the metadata and the latter all the datapoints.


.. codeauthor::
    Nicolas Vetsch,
    Peter Kraus
"""

from pathlib import Path
from xarray import DataTree, Dataset
from yadg.dgutils import dateutils
from yadg.dgutils.table import process_table
from yadg.extractors import get_extract_dispatch
from yadg.extractors.panalytical.common import panalytical_comment, snake_case


extract = get_extract_dispatch()


def process_comments(comments: list[str]) -> dict:
    ret = {}
    for line in comments:
        ret.update(panalytical_comment(line))
    return ret


def process_header(header: str) -> dict:
    """
    Processes the header section, staring with the ``[Measurement conditions]`` line.

    Parameters
    ----------
    header
        The header portion as a string.

    Returns
    -------
    header: dict
        A dictionary containing the processed metadata.

    """
    header_lines = header.split("\n")[1:-1]
    header = dict([line.split(",", 1) for line in header_lines])
    # Process comment entries.
    comments = []
    for key in list(header.keys()):
        if key.startswith("Comment"):
            comments.append(header.pop(key).strip('"'))
    comments = process_comments(comments)
    # Renaming the keys.
    for key in list(header.keys()):
        header[snake_case(key)] = header.pop(key)
    header.update(comments)
    return header


def process_data(data: str) -> tuple[list, list]:
    """
    Processes the data section, starting with the ``[Scan points]`` line.

    Parameters
    ----------
    data
        The data portion as a string.

    Returns
    -------
    avals, adevs, ivals, idevs
        The values and uncertainties in angle and intensity.

    """
    data_lines = data.split("\n")[1:-1]
    columns = data_lines[0].split(",")
    assert columns == ["Angle", "Intensity"], "Unexpected columns."
    data_vars = process_table(
        lines=data_lines[1:],
        headers=["angle", "intensity"],
        sep=",",
    )
    data_vars["intensity"] = (
        ["uts", "angle"],
        [data_vars["intensity"][1]],
        data_vars["intensity"][2],
    )
    coords = dict(angle=data_vars.pop("angle"))
    return data_vars, coords


@extract.register(Path)
def extract_from_path(
    source: Path,
    *,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(source, "r", encoding=encoding) as csv_file:
        csv = csv_file.read()
    # Split file into its sections.
    __, header, data = csv.split("[")
    assert header.startswith("Measurement conditions"), "Unexpected section."
    assert data.startswith("Scan points"), "Unexpected section."
    header = process_header(header)
    # Process the data trace.
    data_vars, coords = process_data(data)
    # Process the metadata.
    uts = dateutils.str_to_uts(
        timestamp=header["file_date_and_time"],
        format="%d/%B/%Y %H:%M",
        timezone=timezone,
    )
    coords["uts"] = (["uts"], [uts])
    header["fulldate"] = True
    ds = Dataset(
        data_vars=data_vars,
        coords=coords,
        attrs=dict(original_metadata=header),
    )
    return DataTree(ds)
