"""
panalyticalxy: Processing of PANalytical XRD ``xy`` files
---------------------------------------------------------

File Structure
``````````````

These files basically just contain the ``[Scan points]`` part of
:mod:`~yadg.parsers.xrdtrace.panalyticalcsv` files. As a consequence, no metadata
is recorded, and the format does not have an associated timestamp.

Uncertainties
`````````````
The uncertainties of ``"angle"`` are taken from the number of significant figures.

The uncertainties of ``"intensity"`` are taken from the number of significant figures.

.. codeauthor::
    Nicolas Vetsch,
    Peter Kraus
"""

from uncertainties.core import str_to_number_with_uncert as tuple_fromstr
import numpy as np
import xarray as xr


def process(
    *,
    fn: str,
    encoding: str,
    **kwargs: dict,
) -> xr.Dataset:
    """Processes a PANalytical XRD xy file.

    Parameters
    ----------
    fn
        The file containing the trace(s) to parse.

    encoding
        Encoding of ``fn``, by default "utf-8".


    Returns
    -------
    :class:`xarray.Dataset`
        Tuple containing the timesteps and metadata. A full timestamp is not available
        in ``.xy`` files.

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
        data_vars={
            "intensity": (
                ["angle"],
                list(insty),
                {"units": "counts", "ancillary_variables": "intensity_std_err"},
            ),
            "intensity_std_err": (
                ["angle"],
                idevs,
                {"units": "counts", "standard_name": "intensity standard_error"},
            ),
            "angle_std_err": (
                ["angle"],
                adiff,
                {"units": "deg", "standard_name": "angle standard_error"},
            ),
        },
        coords={
            "angle": (
                ["angle"],
                list(angle),
                {"units": "deg", "ancillary_variables": "angle_std_err"},
            ),
        },
    )
    return vals
