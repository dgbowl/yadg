"""

"""

import re
from collections import defaultdict
from datetime import datetime
from typing import Union
from xml.etree import ElementTree


# Recursively parsing etree into a python dictionary.
# From https://stackoverflow.com/a/10076823.
def etree_to_dict(e: ElementTree.Element) -> dict:
    """"""
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


# Converting camelCase xrdml keys to snake_case.
# From https://stackoverflow.com/a/1176023
def snake_case(camelCase: str) -> str:
    """
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camelCase).lower()


def _parse_values(d: Union[dict, list]) -> dict:
    """Recursively parses values from subdicts.
    
    Values in
    
    """
    # TODO
    # If key does not start with @ or is not #text just snake_case val
    # If key is #text then combine it with the keys starting with @
    # If key starts with @ then combine and is no @unit or @version,
    # then just strip @
    if d.keys() == ["@unit", "#text"]:
        # TODO
        pass
    else:
        for key, value in d:
            # TODO
            pass
    return {}


def _parse_scan(scan: dict) -> dict:
    """
    
    """
    header = scan.pop("header")
    uts = datetime.fromisoformat(header.pop("startTimeStamp"))

    datapoints = scan.pop("dataPoints")
    datapoints["positions"] = _parse_values(datapoints["positions"])
    datapoints["counting_time"] = _parse_values(datapoints.pop("commonCountingTime"))
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
    wavelength = _parse_values(measurement.pop("usedWavelength"))
    measurement["wavelength"] = wavelength
    # Incident beam path.
    incident_beam_path = _parse_values(measurement.pop("incidentBeamPath"))
    measurement["incident_beam_path"] = incident_beam_path
    # Diffracted beam path.
    diffracted_beam_path = _parse_values(measurement.pop("diffractedBeamPath"))
    measurement["diffracted_beam_path"] = diffracted_beam_path

    scan = _parse_scan(measurement.pop("scan"))

    return measurement


def process(fn: str):
    """
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
    assert measurements["@status"] == "Completed"
    comment = _process_comment(measurements["comment"])
    # Renaming some entries.
    sample = measurements["sample"]
    sample["prepared_by"] = sample.pop("preparedBy")
    sample["type"] = sample.pop("@type")
    # Process measurement data.
    measurement = _process_measurement(measurements["xrdMeasurement"])

    timesteps = [{"uts": None, "fn": fn, "raw": None}]

    return timesteps


if __name__ == "__main__":
    path = (
        r"G:\Collaborators\Vetsch Nicolas\parsers\xrd\testing\210520step1_30min.xrdml"
    )
    process(path)
    print("")
