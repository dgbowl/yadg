"""Processing of PANalytical XRD csv files.

File Structure
``````````````

These files are split into a ``[Measurement conditions]`` and a
``[Scan points]`` section. The former stores the metadata and the latter
all the datapoints.


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

.. codeauthor:: Nicolas Vetsch <vetschnicolas@gmail.com>
"""

import re
from datetime import datetime


# Converting camelCase xrdml keys to snake_case.
def snake_case(s: str) -> str:
    """Converts Sentence case. and camelCase strings to snake_case.

    From https://stackoverflow.com/a/1176023

    Parameters
    ----------
    s
        The input string to be converted.

    Returns
    -------
    str
        The corresponding snake_case string.

    """
    s = "".join([s.capitalize() for s in s.replace(".", "").split()])
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def _process_comments(comments: list[str]) -> dict:
    """Processes the list of comments from the file header.

    Parameters
    ----------
    comments
        A list containing all the present comment lines.

    Returns
    -------
    dict
        A dictionary containing the processed comments.

    """
    processed_comments = {}
    for line in comments:
        if line.startswith("Configuration="):
            split = [s.split("=") for s in line.split(", ")]
            __, values = list(zip(*split))
            keys = ["configuration", "owner", "creation_date"]
        elif line.startswith("Goniometer="):
            split = [s.replace("=", ":").split(":") for s in line.split(";")]
            __, values = list(zip(*split))
            keys = ["goniometer", "min_step_size_2theta", "min_step_size_omega"]
        elif line.startswith("Sample stage="):
            __, values = line.split("=")
            keys = ["sample_stage"]
        elif line.startswith("Diffractometer system="):
            __, values = line.split("=")
            keys = ["diffractometer_system"]
        elif line.startswith("Measurement program="):
            split = [s.split("=") for s in line.split(", ")]
            __, values = list(zip(*split))
            keys = ["measurement_program", "identifier"]
        elif line.startswith("Fine Calibration Offset for 2Theta"):
            __, values = line.split(" = ")
            keys = ["calib_offset_2theta"]
        else:
            raise NotImplementedError(f"Unrecognized comment line: {line}")
        values = [values] if isinstance(values, str) else values
        processed_comments.update(dict(zip(keys, values)))
    return processed_comments


def _process_header(header: str) -> dict:
    """Processes the header (``[Measurement conditions]``) section.

    Parameters
    ----------
    header
        The header portion as a string.

    Returns
    -------
    header : dict
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
    """Processes the data (``[Scan points]``) section.

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
    """Processes a PANalytical XRD csv file.

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
    # Process the data trace.
    angle, intensity = _process_data(data)
    angle = {
        "n": angle,
        "s": [float(header["scan_step_size"])] * len(angle),
        "u": "deg",
    }
    # TODO: Not sure about hte accuracy here. The counts are resolved as
    # integers.
    intensity = {
        "n": intensity,
        "s": [1.0] * len(intensity),
        "u": "counts",
    }
    # Process the metadata.
    meta = _process_header(header)
    uts = datetime.strptime(meta["file_date_and_time"], "%d/%B/%Y %H:%M").timestamp()
    traces = {"0": {"angle": angle, "intensity": intensity}}
    data = [{"fn": fn, "uts": uts, "traces": traces}]
    return data, meta, True
