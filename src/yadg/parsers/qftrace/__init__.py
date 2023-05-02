"""
The module handles the reading and processing of the network analyzer
traces, containing the reflection coefficient as a function of the sweeped frequency,
:math:`\\Gamma(f)`.

:mod:`~yadg.parsers.qftrace` loads the reflection trace data, determines the
uncertainties of the signal (y-axis), and explicitly populates the points in
the time axis (x-axis).

Usage
`````
Available since ``yadg-3.0``. The parser supports the following parameters:

.. _yadg.parsers.qftrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.QFTrace

.. _yadg.parsers.qftrace.formats:

 - LabView output in a tab-separated format (``csv``):
   :mod:`~yadg.parsers.qftrace.labviewcsv`

.. _yadg.parsers.qftrace.provides:

Schema
``````
For filetypes containing the reflection trace data, the schema is as follows:

.. code-block:: yaml

  datatree.DataTree:
    S11:
      coords:
        uts:        !!float
        freq:       !!float       # Field frequency (Hz)
      data_vars:
        Re(G):      (uts, freq)   # Imaginary part of the reflection coefficient
        Im(G)       (uts, freq)   # Real part of the reflection coefficient
        average:    (uts)         # Number of scans averaged to form a single trace
        bandwidth:  (uts)         # Filter bandwidth (Hz)

Module Functions
````````````````

"""
from . import labviewcsv
import datatree


def process(
    *,
    filetype: str,
    **kwargs: dict,
) -> datatree.DataTree:
    """
    VNA reflection trace parser. Forwards ``kwargs`` to the worker functions
    based on the supplied ``filetype``.

    Parameters
    ----------
    filetype
        Discriminator used to select the appropriate worker function.

    Returns
    -------
    :class:`datatree.DataTree`

    """
    if filetype == "labview.csv":
        return labviewcsv.process(**kwargs)
