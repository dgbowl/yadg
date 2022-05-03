"""
panalyticalcsv: Processing of PANalytical XRD ``csv`` files
-----------------------------------------------------------

File Structure
``````````````

These files are split into a ``[Measurement conditions]`` and a ``[Scan points]`` 
section. The former stores the metadata and the latter all the datapoints. 

.. warning::
    
    This parser is fairly new and untested. As a result, the returned metadata 
    contain all the entries in the ``[Measurement conditions]`` section, without 
    any additional filtering.


Structure of Parsed Timesteps
`````````````````````````````

.. code-block:: yaml

    - fn:  !!str
    - uts: !!float
    - raw:
        traces:
          "{{ trace_number }}":  # Number of the trace.
            angle:               # Diffraction angle.
              {n: [!!float, ...], s: [!!float, ...], u: "deg"}
            intensity:           # Detector counts.
              {n: [!!float, ...], s: [!!float, ...], u: "counts"}

.. codeauthor:: Nicolas Vetsch
"""

from ...dgutils import dateutils
from .common import panalytical_comment, snake_case

# Converting camelCase xrdml keys to snake_case.


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
    header = dict([l.split(",", 1) for l in header_lines])
    # Process comment entries.
    comments = []
    for key in list(header.keys()):
        if key.startswith("Comment"):
            comments.append(header.pop(key).strip('"'))
    comments = _process_comments(comments)
    # Renaming the keys.
    for key in list(header.keys()):
        header[snake_case(key)] = header.pop(key)
    header["comments"] = comments
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
    (angle, intensity) : tuple[list, list]
        A list containing the angle data and one containing the
        intensity counts.

    """
    data_lines = data.split("\n")[1:-1]
    columns = data_lines[0].split(",")
    assert columns == ["Angle", "Intensity"], "Unexpected columns."
    datapoints = [l.split(",") for l in data_lines[1:]]
    angle, intensity = [list(d) for d in zip(*datapoints)]
    angle = [float(a) for a in angle]
    intensity = [float(i) for i in intensity]
    return angle, intensity


def process(
    fn: str, encoding: str = "utf-8", timezone: str = "UTC"
) -> tuple[list, dict, bool]:
    """
    Processes a PANalytical XRD csv file. All information contained in the header
    of the csv file is stored in the metadata.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "UTC".

    Returns
    -------
    (data, meta) : tuple[list, dict]
        (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and the full date tag.
        For .csv files tag is specified.

    """
    with open(fn, "r", encoding=encoding) as csv_file:
        csv = csv_file.read()
    # Split file into its sections.
    __, header, data = csv.split("[")
    assert header.startswith("Measurement conditions"), "Unexpected section."
    assert data.startswith("Scan points"), "Unexpected section."
    header = _process_header(header)
    # Process the data trace.
    angle, intensity = _process_data(data)
    angle = {
        "n": angle,
        "s": [float(header["scan_step_size"])] * len(angle),
        "u": "deg",
    }
    intensity = {
        "n": intensity,
        "s": [1.0] * len(intensity),
        "u": "counts",
    }
    # Process the metadata.
    uts = dateutils.str_to_uts(
        header["file_date_and_time"], format="%d/%B/%Y %H:%M", timezone=timezone
    )
    traces = {"0": {"angle": angle, "intensity": intensity}}
    data = [{"fn": fn, "uts": uts, "raw": {"traces": traces}}]
    return data, header, True
