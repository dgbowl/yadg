"""
panalyticalxrdml: Processing of PANalytical XRD ``xml`` files
-------------------------------------------------------------

File Structure
``````````````

These are xml-formatted files, which we here parse using the :mod:`xml.etree`
library into a Python :class:`dict`.

.. note::
    
    The ``angle`` returned from this parser is based on a linear interpolation of
    the start and end point of the scan, and is the :math:`2\\theta`. The values
    of :math:`\\omega` are discarded.

.. warning::
    
    This parser is fairly new and untested. As a result, the returned metadata 
    contain only a subset of the available metadata in the XML file. If something
    important is missing, please contact us!

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

.. codeauthor:: 
    Nicolas Vetsch,
    Peter Kraus
"""

from collections import defaultdict
from typing import Union
from xml.etree import ElementTree
import numpy as np

from .common import panalytical_comment
from ...dgutils import dateutils


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
        "timestamp": header.pop("startTimeStamp"),
        "intensities": intensities,
        "counting_time": counting_time,
    }

    positions = _process_values(datapoints.pop("positions"))
    for v in positions:
        pos = np.linspace(
            float(v["startPosition"]), float(v["endPosition"]), num=len(raw_intensities)
        )
        dp[v["@axis"]] = {
            "n": list(pos),
            "s": [pos[1] - pos[0]] * len(pos),
            "u": v["@unit"],
        }
    return dp


def _process_comment(comment: dict) -> dict:
    """ """
    entry = comment.pop("entry")
    ret = {}
    for line in entry:
        ret.update(panalytical_comment(line))
    return ret


def _process_measurement(measurement: dict, timezone: str):
    """
    A function that processes each section of the XRD XML file.
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
        "uts": dateutils.str_to_uts(scan.pop("timestamp"), timezone=timezone),
        "raw": {"traces": {"0": trace}},
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
    data, meta = _process_measurement(measurements["xrdMeasurement"], timezone)
    data["fn"] = fn
    # Shove unused data into meta
    meta["sample"] = sample
    meta["comment"] = comment
    return [data], meta, True
