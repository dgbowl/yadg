import re


def panalytical_comment(line: str) -> dict:
    """Processes a comments from the file header into a dictionary.

    Parameters
    ----------
    line
        A line containing the comment.

    Returns
    -------
    dict
        A dictionary containing the processed comment.

    """

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
    values = [values] if isinstance(values, str) else values
    return dict(zip(keys, values))


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
