"""
Handles processing of Panalytical XRDML files.

Usage
`````
Available since ``yadg-4.2``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.Panalytical_xrdml

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
The following metadata is extracted:

  - ``sample``: Metadata information about the sample.
  - ``wavelength``: Measurement wavelength.
  - ``comment``: A free-form description of the experiment.
  - ``incident_beam_path``
  - ``diffracted_beam_path``
  - ``counting_time``

.. note::

    The returned metadata contain only a subset of the available metadata in the XML
    file. If something important is missing, please contact us!

Notes on file structure
```````````````````````
These are xml-formatted files, which we here parse using the :mod:`xml.etree`
library into a Python :class:`dict`.

The ``angle`` returned from this parser is based on a linear interpolation of the start
and end point of the scan, and is the :math:`2\\theta`. The values of :math:`\\omega`
are discarded.

Uncertainties
`````````````
The uncertainties of in ``"angle"`` are taken as the step-width of the linearly spaced
:math:`2\\theta` values.

The uncertainties of of ``"intensity"`` are currently set to a constant
value of 1.0 count as all the supported files seem to produce integer values.

.. codeauthor::
    Nicolas Vetsch,
    Peter Kraus

"""

from collections import defaultdict
from typing import Union
from xml.etree import ElementTree
import numpy as np
from datatree import DataTree
import xarray as xr
from uncertainties.core import str_to_number_with_uncert as tuple_fromstr

from yadg.extractors.panalytical.common import panalytical_comment
from yadg.dgutils import dateutils


def etree_to_dict(e: ElementTree.Element) -> dict:
    """Recursively converts an ElementTree.Element into a dictionary.

    Element attributes are stored into `"@"`-prefixed attribute keys.
    Element text is stored into `"#text"` for all nodes.

    From https://stackoverflow.com/a/10076823.
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
    dpts = scan.pop("dataPoints")
    counting_time = _process_values(dpts.pop("commonCountingTime"))
    ivals, idevs = list(
        zip(*[tuple_fromstr(c) for c in dpts["intensities"].pop("#text").split()])
    )
    iunit = dpts["intensities"].pop("@unit")
    timestamp = header.pop("startTimeStamp")

    dp = {
        "intensity": {"vals": ivals, "devs": idevs, "unit": iunit},
        "timestamp": timestamp,
        "counting_time": counting_time,
    }

    positions = _process_values(dpts.pop("positions"))
    for v in positions:
        pos = np.linspace(
            float(v["startPosition"]), float(v["endPosition"]), num=len(ivals)
        )
        adiff = np.abs(np.diff(pos)) * 0.5
        adiff = np.append(adiff, adiff[-1])
        dp[v["@axis"]] = {
            "vals": pos,
            "devs": adiff,
            "unit": v["@unit"],
        }
    return dp


def _process_comment(comment: dict) -> dict:
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
    trace = {"angle": scan.pop("2Theta"), "intensity": scan.pop("intensity")}
    meta = measurement
    meta["counting_time"] = scan.pop("counting_time")
    trace["uts"] = dateutils.str_to_uts(
        timestamp=scan.pop("timestamp"), timezone=timezone
    )
    return trace, meta


def extract(
    *,
    fn: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
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
    meta["fulldate"] = True
    # Build Datasets
    vals = xr.Dataset(
        data_vars={
            "intensity": (
                ["uts", "angle"],
                np.reshape(data["intensity"]["vals"], (1, -1)),
                {
                    "units": data["intensity"]["unit"],
                    "ancillary_variables": "intensity_std_err",
                },
            ),
            "intensity_std_err": (
                ["uts", "angle"],
                np.reshape(data["intensity"]["devs"], (1, -1)),
                {
                    "units": data["intensity"]["unit"],
                    "standard_name": "intensity standard_error",
                },
            ),
            "angle_std_err": (
                ["uts", "angle"],
                np.reshape(data["angle"]["devs"], (1, -1)),
                {
                    "units": data["angle"]["unit"],
                    "standard_name": "angle standard_error",
                },
            ),
        },
        coords={
            "uts": (["uts"], [data["uts"]]),
            "angle": (
                ["angle"],
                data["angle"]["vals"],
                {
                    "units": data["angle"]["unit"],
                    "ancillary_variables": "angle_std_err",
                },
            ),
        },
        attrs=dict(original_metadata=meta),
    )
    return DataTree(vals)
