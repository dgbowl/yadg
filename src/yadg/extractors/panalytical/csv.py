"""
Handles processing of csv exports of Panalytical XRD files.

Usage
`````
Available since ``yadg-4.2``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Panalytical_csv

Schema
``````
.. code-block:: yaml

    datatree.DataTree:
      coords:
        uts:            !!float               # Unix timestamp
        angle:          !!float               # 2θ angle
      data_vars:
        intensity:      (uts, angle)          # Measured intensity

Metadata
````````
With the exception of the ``comment``, the metadata present in the csv file is extracted
from the file header without post-processing.

Notes on file structure
```````````````````````
These files are split into a ``[Measurement conditions]`` and a ``[Scan points]``
section. The former stores the metadata and the latter all the datapoints.

Uncertainties
`````````````
The uncertainties of ``"angle"`` are taken from the number of significant figures.

The uncertainties of ``"intensity"`` are taken from the number of significant figures.

.. codeauthor::
    Nicolas Vetsch,
    Peter Kraus
"""

from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
from datatree import DataTree
import xarray as xr
import numpy as np

from yadg.dgutils import dateutils
from yadg.extractors.panalytical.common import panalytical_comment, snake_case


def _process_comments(comments: list[str]) -> dict:
    ret = {}
    for line in comments:
        ret.update(panalytical_comment(line))
    return ret


def _process_header(header: str) -> dict:
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
    comments = _process_comments(comments)
    # Renaming the keys.
    for key in list(header.keys()):
        header[snake_case(key)] = header.pop(key)
    header.update(comments)
    return header


def _process_data(data: str) -> tuple[list, list]:
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
    datapoints = [line.split(",") for line in data_lines[1:]]
    angle, intensity = [list(d) for d in zip(*datapoints)]
    avals, adevs = list(zip(*[tuple_fromstr(a) for a in angle]))
    ivals, idevs = list(zip(*[tuple_fromstr(i) for i in intensity]))
    return avals, adevs, ivals, idevs


def extract(
    *,
    fn: str,
    encoding: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    with open(fn, "r", encoding=encoding) as csv_file:
        csv = csv_file.read()
    # Split file into its sections.
    __, header, data = csv.split("[")
    assert header.startswith("Measurement conditions"), "Unexpected section."
    assert data.startswith("Scan points"), "Unexpected section."
    header = _process_header(header)
    # Process the data trace.
    angle, _, insty, _ = _process_data(data)
    adiff = np.abs(np.diff(angle)) * 0.5
    adiff = np.append(adiff, adiff[-1])
    idevs = np.ones(len(insty))
    # Process the metadata.
    uts = dateutils.str_to_uts(
        timestamp=header["file_date_and_time"],
        format="%d/%B/%Y %H:%M",
        timezone=timezone,
    )
    header["fulldate"] = True
    # Build Datasets
    vals = xr.Dataset(
        data_vars={
            "intensity": (
                ["uts", "angle"],
                np.reshape(insty, (1, -1)),
                {"units": "counts", "ancillary_variables": "intensity_std_err"},
            ),
            "intensity_std_err": (
                ["uts", "angle"],
                np.reshape(idevs, (1, -1)),
                {"units": "counts", "standard_name": "intensity standard_error"},
            ),
            "angle_std_err": (
                ["uts", "angle"],
                np.reshape(adiff, (1, -1)),
                {"units": "deg", "standard_name": "angle standard_error"},
            ),
        },
        coords={
            "uts": (["uts"], [uts]),
            "angle": (
                ["angle"],
                list(angle),
                {"units": "deg", "ancillary_variables": "angle_std_err"},
            ),
        },
        attrs=dict(original_metadata=header),
    )
    return DataTree(vals)
