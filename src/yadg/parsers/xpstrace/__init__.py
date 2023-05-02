"""
This module handles the reading and processing of X-ray photoelectron spectroscopy
data, including determining the uncertainties of the signal (y-axis), and explicitly
populating the points in the energy axis (``E``).

Usage
`````
Available since ``yadg-4.1``. The parser supports the following parameters:

.. _yadg.parsers.xpstrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.XPSTrace

.. _yadg.parsers.xpstrace.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - ULVAC PHI Multipak XPS traces (``phi.spe``),
   see :mod:`~yadg.parsers.xpstrace.phispe`

.. _yadg.parsers.xpstrace.provides:

Provides
````````
The raw data is stored, for each timestep, using the following format:

.. code-block:: yaml

  datatree.DataTree:
    {{ trace_name }}      !!xr.Dataset
      coords:
        uts:              !!float
        E:                !!float      # binding energies (eV)
      data_vals:
        y:                (uts, E)     # signal

Module Functions
````````````````

"""
import datatree
from . import phispe


def process(
    *,
    filetype: str,
    **kwargs: dict,
) -> datatree.DataTree:
    """
    Unified x-ray photoelectron spectroscopy parser. Forwards ``kwargs`` to the worker
    functions based on the supplied ``filetype``.

    This parser processes XPS scans in signal(energy) format.

    Parameters
    ----------
    filetype
        Discriminator used to select the appropriate worker function.

    Returns
    -------
    :class:`datatree.DataTree`

    """
    if filetype == "phi.spe":
        return phispe.process(**kwargs)
