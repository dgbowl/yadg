"""
panalyticalxy: Processing of PANalytical XRD ``xy`` files
---------------------------------------------------------

File Structure
``````````````

These files basically just contain the ``[Scan points]`` part of PANalytical csv
files :mod:`yadg.parsers.xrdtrace.panalyticalcsv`. As a consequence, no metadata
is recorded, and the format does not have an associated timestamp.


DataTree structure
``````````````````

.. code-block::

    /:
        Dimensions:    (uts: 1, angle: n)
        Coordinates:
            uts:       (uts)            float64     Timestamp, set to 0.0.
            angle:     (angle)          float64     Diffraction angle, degrees.
        Data variables:
            intensity  (uts, angle)     float64     Detector intensity, counts.
        Attributes:    
    /_yadg.meta:
        Dimensions:    (uts: 1, _angle: n)
        Coordinates:
            uts:       (uts)            float64 
            _angle:    (_angle)         float64
        Data variables:
            intensity  (uts, _angle)    float64     Dev. of intensity, counts.
            angle      (uts, _angle)    float64     Dev. of angle, degrees.
            _fn        (uts)            str         Filename of the datapoint

.. codeauthors:: 
    Nicolas Vetsch,
    Peter Kraus
"""

from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import numpy as np
import xarray as xr
from zoneinfo import ZoneInfo


def process(
    fn: str,
    encoding: str,
    timezone: ZoneInfo,
) -> tuple[xr.Dataset, xr.Dataset]:
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
    DataTree : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and the full date tag.
        For .xy files tag is never specified.

    """
    with open(fn, "r", encoding=encoding) as xy_file:
        xy = xy_file.readlines()
    datapoints = [li.strip().split() for li in xy]
    angle, intensity = list(zip(*datapoints))
    angle, _ = list(zip(*[tuple_fromstr(a) for a in angle]))
    insty, _ = list(zip(*[tuple_fromstr(i) for i in intensity]))
    idevs = np.ones(len(insty))
    adiff = np.abs(np.diff(angle)) * 0.5
    adiff = np.append(adiff, adiff[-1])

    vals = xr.Dataset(
        data_vars=dict(
            intensity=(
                ["uts", "angle"],
                np.reshape(insty, (1, -1)),
                {"units": "counts"},
            )
        ),
        coords=dict(
            angle=(
                ["angle"],
                list(angle),
                {"units": "deg"},
            ),
        ),
        attrs=dict(fulldate=False),
    )
    devs = xr.Dataset(
        data_vars=dict(
            intensity=(
                ["_uts", "_angle"],
                np.reshape(idevs, (1, -1)),
                {"units": "counts"},
            ),
            angle=(
                ["_uts", "_angle"],
                np.reshape(adiff, (1, -1)),
                {"units": "deg"},
            ),
            _fn=(
                ["_uts"],
                [str(fn)],
            ),
        ),
        coords=dict(
            _angle=(["_angle"], list(angle), {"units": "deg"}),
        ),
    )
    return vals, devs
