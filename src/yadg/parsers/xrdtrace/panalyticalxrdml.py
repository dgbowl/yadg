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


def _process_values(d: Union[dict, str]) -> dict:
    """Recursively parses values from subdicts.
    
    Parameters
    ----------
    d

    
    """
    # TODO
    # If not "#text" or @tribute just snake_case and recurse.
    # If "@unit", append unit to all non-attribute vals.
    # If "#text" and ("@unit" or "@version") conbine the two.
    if isinstance(d, str):
        return d
    
    if "@unit" in d:
        if "#text" in d:
            return " ".join(d["#text"], d["@unit"])
        for key in [k]
    else:
        for key, value in d:
            # TODO
            pass
    return {}


def _process_scan(scan: dict) -> dict:
    """Parses the scan section of the file.
    
    Parameters
    ----------
    scan
        The scan dictionary.
        
    Returns
    -------
    dict
        The processed
    
    """
    header = scan.pop("header")
    uts = datetime.fromisoformat(header.pop("startTimeStamp"))
    datapoints = scan.pop("dataPoints")
    datapoints["positions"] = _process_values(datapoints["positions"])
    datapoints["counting_time"] = _process_values(datapoints.pop("commonCountingTime"))
    datapoints["counts"] = {
        "n": [float(c) for c in datapoints["counts"].split()],
        "s": [],
        "u": datapoints["counts"]["@unit"],
    }
    return datapoints


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
    __, values = list(zip(*[s.split(" = ") for s in comment.split(", ")]))
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

    return measurement


def process(
    fn: str, encoding: str = "utf-8", timezone: str = "localtime"
) -> tuple[list, dict, bool]:
    """Processes a PANalytical XRD csv file.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

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
    measurement = _process_measurement(measurements["xrdMeasurement"])

    # TODO Process timestamps.
    timesteps = [{"uts": None, "fn": fn, "raw": None}]

    return data, meta, True
