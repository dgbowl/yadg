"""Processing of PANalytical XRD csv files.

TODO

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
from collections import defaultdict
from datetime import datetime
from typing import Union
from xml.etree import ElementTree
import numpy as np


# Recursively parsing etree into a python dictionary.
def etree_to_dict(e: ElementTree.Element) -> dict:
    """Recursively converts an ElementTree.Element into a dictionary.
    
    Element attributes are stored into `"@"`-prefixed attribute keys.
    Element text is stored into `"#text"` for all nodes.
    
    From https://stackoverflow.com/a/10076823.
    
    Parameters
    ----------
    e
        The ElementTree root Element.
        
    Returns
    -------
    dict
        ElementTree parsed into a dictionary.
    
    """
    d = {e.tag: {} if e.attrib else None}
    children = list(e)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {e.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if e.attrib:
        d[e.tag].update(("@" + k, v) for k, v in e.attrib.items())
    if e.text:
        text = e.text.strip()
        if children or e.attrib:
            if text:
                d[e.tag]["#text"] = text
        else:
            d[e.tag] = text
    return d


def snake_case(s: str) -> str:
    """Converts camelCase xrdml keys to snake_case.
    
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
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def _process_values(d: Union[dict, str]) -> Union[dict, str]:
    """
    Recursively parses dicts in the following format:
    
    .. code:: 

        {"key": {"#text": ..., "@unit": ...}, ...}
    
    into a single string:

    .. code:: 

        {"key": f"{#text} {@unit}", ...}
    
    """
    # TODO
    # If not "#text" or @tribute just snake_case and recurse.
    if isinstance(d, dict):
        if "@unit" in d and "#text" in d:
            return f"{d['#text']} {d['@unit']}"
        elif "@version" in d and "#text" in d:
            return f"{d['#text']} {d['@version']}"
        else:
            for k, v in d.items():
                d[k] = _process_values(v)
    return d


def _process_scan(scan: dict) -> dict:
    """
    Parses the scan section of the file. Creates the explicit positions based 
    on the number of measured intensities and the start & end position.
    
    """
    header = scan.pop("header")
    datapoints = scan.pop("dataPoints")
    counting_time = _process_values(datapoints.pop("commonCountingTime"))
    raw_intensities = [float(c) for c in datapoints["intensities"].pop("#text").split()]
    intensities = {
        "n": raw_intensities,
        "s": [1.0] * len(raw_intensities),
        "u": datapoints["intensities"].pop("@unit"),
    }
    dp = {
        "uts": datetime.fromisoformat(header.pop("startTimeStamp")).timestamp(),
        "intensities": intensities,
        "counting_time": counting_time
    }
    
    positions = _process_values(datapoints.pop("positions"))
    for v in positions:
        pos = np.linspace(
            float(v["startPosition"]), 
            float(v["endPosition"]),
            num = len(raw_intensities)
        )
        dp[v["@axis"]] = {
            "n": list(pos),
            "s": [pos[1]-pos[0]] * len(pos),
            "u": v["@unit"]
        }
    return dp


def _process_comment(comment: dict) -> dict:
    """
    """
    entry = comment.pop("entry")
    for line in entry:
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
        comment.update(dict(zip(keys, values)))
    return comment


def _process_measurement(measurement: dict):
    """
    """
    # Comment.
    comment = measurement["comment"].pop("entry")
    for line in comment:
        if "PHD Lower Level" in line and "PHD Upper Level" in line:
            __, values = list(zip(*[s.split(" = ") for s in line.split(", ")]))
    keys = ["phd_lower_level", "phd_upper_level"]
    measurement["comment"] = dict(zip(keys, values))
    # Wavelength.
    wavelength = _process_values(measurement.pop("usedWavelength"))
    measurement["wavelength"] = wavelength
    # Incident beam path.
    incident_beam_path = _process_values(measurement.pop("incidentBeamPath"))
    measurement["incident_beam_path"] = incident_beam_path
    # Diffracted beam path.
    diffracted_beam_path = _process_values(measurement.pop("diffractedBeamPath"))
    measurement["diffracted_beam_path"] = diffracted_beam_path
    scan = _process_scan(measurement.pop("scan"))
    trace = {"angle": scan.pop("2Theta"), "intensity": scan.pop("intensities")}
    meta = measurement
    meta["counting_time"] = scan.pop("counting_time")
    data = {
        "uts": scan.pop("uts"),
        "raw": {"traces": {"0": trace}}
    }
    return data, meta


def process(
    fn: str, encoding: str = "utf-8", timezone: str = "UTC"
) -> tuple[list, dict, bool]:
    """Processes a PANalytical xrdml file.

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
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and the full date tag.
        For .xrdml tag is always specified

    """
    # TODO: Maybe validate the xrdml file against the specified xml
    # schema. This would however require `lxml` and add another
    # dependency to yadg.
    it = ElementTree.iterparse(fn)
    # Removing xmlns prefixes from all tags.
    # From https://stackoverflow.com/a/25920989.
    for __, e in it:
        __, xmlns_present, postfix = e.tag.partition("}")
        if xmlns_present:
            e.tag = postfix  # Strip away all xmlns prefixes.
    root = it.root
    xrd = etree_to_dict(root)
    # Start processing the xml contents.
    measurements = xrd["xrdMeasurements"]
    assert measurements["@status"] == "Completed", "Incomplete measurement."
    comment = _process_comment(measurements["comment"])
    # Renaming some entries because I want to.
    sample = measurements["sample"]
    sample["prepared_by"] = sample.pop("preparedBy")
    sample["type"] = sample.pop("@type")
    # Process measurement data.
    data, meta = _process_measurement(measurements["xrdMeasurement"])
    data["fn"] = fn
    return [data], meta, True
