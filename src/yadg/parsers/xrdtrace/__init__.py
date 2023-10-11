"""
This module handles the reading and processing of X-ray diffraction data. It loads X-ray
diffraction data, determines reasonable uncertainties of the signal intensity (y-axis),
and explicitly populates the angle axis (:math:`2\\theta`), if necessary.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.xrdtrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.XRDTrace

.. _yadg.parsers.xrdtrace.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - PANalytical ``xrdml`` files (``panalytical.xrdml``),
   see :mod:`~yadg.parsers.xrdtrace.panalyticalxrdml`
 - PANalytical ``csv`` files (``panalytical.csv``),
   see :mod:`~yadg.parsers.xrdtrace.panalyticalcsv`
 - PANalytical ``xy`` files (``panalytical.xy``),
   see :mod:`~yadg.parsers.xrdtrace.panalyticalxy`

.. _yadg.parsers.xrdtrace.provides:

Provides
````````
The raw data is stored, for each timestep, using the following format:

.. code-block:: yaml

  xr.Dataset:
    coords:
      uts:         !!float
      angle:       !!float            # Diffraction angle (deg)
    data_vals:
      intensity:   (uts, angle)       # Detector intensity (counts)

"""
import xarray as xr
from . import panalyticalxrdml, panalyticalcsv, panalyticalxy


def process(
    *,
    filetype: str,
    **kwargs: dict,
) -> xr.Dataset:
    """
    Unified X-ray diffractogram data parser. Forwards ``kwargs`` to the worker
    functions based on the supplied ``filetype``.

    This parser processes XPS scans in signal(energy) format.

    Parameters
    ----------
    filetype
        Discriminator used to select the appropriate worker function.

    Returns
    -------
    :class:`xarray.Dataset`


    """
    if filetype == "panalytical.xrdml":
        return panalyticalxrdml.process(**kwargs)
    elif filetype == "panalytical.csv":
        return panalyticalcsv.process(**kwargs)
    elif filetype == "panalytical.xy":
        return panalyticalxy.process(**kwargs)
