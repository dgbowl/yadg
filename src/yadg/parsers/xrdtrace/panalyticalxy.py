"""
panalyticalxy: Processing of PANalytical XRD ``xy`` files
---------------------------------------------------------

File Structure
``````````````

These files basically just contain the ``[Scan points]`` part of PANalytical csv 
files :mod:`yadg.parsers.xrdtrace.panalyticalcsv`. As a consequence, no metadata
is recorded, and the format does not have an associated timestamp.


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


def process(
    fn: str, encoding: str = "utf-8", timezone: str = "UTC"
) -> tuple[list, dict, bool]:
    """Processes a PANalytical XRD xy file.

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
        For .xy files tag is never specified.

    """
    with open(fn, "r", encoding=encoding) as xy_file:
        xy = xy_file.read()
    datapoints = [l.split() for l in xy.split("\n")[:-1]]
    angle, intensity = list(zip(*datapoints))
    angle = [float(a) for a in angle]
    intensity = [float(i) for i in intensity]
    scan_step_size = angle[1] - angle[0]
    angle = {
        "n": angle,
        "s": [scan_step_size] * len(angle),
        "u": "deg",
    }
    intensity = {
        "n": intensity,
        "s": [1.0] * len(intensity),
        "u": "counts",
    }
    traces = {"0": {"angle": angle, "intensity": intensity}}
    data = [{"fn": fn, "raw": {"traces": traces}}]
    meta = {}
    return data, meta, False
