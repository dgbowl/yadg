"""
Handles the reading and processing of mass spectrometry files. The basic function of the
parser is to:

#. read in the raw data and create timestamped traces with one :class:`xarray.Dataset` per trace
#. collect `metadata` such as the software version, author, etc.

Usage
`````
Select :mod:`~yadg.parsers.masstrace` by supplying it to the ``parser`` keyword
in the `dataschema`. The parser supports the following parameters:

.. _yadg.parsers.masstrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.MassTrace

.. _yadg.parsers.masstrace.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - Pfeiffer Quadstar 32-bit scan analog data (``quadstar.sac``),
   see :mod:`~yadg.parsers.masstrace.quadstarsac`

.. _yadg.parsers.masstrace.provides:

Schema
``````
The raw data, loaded from the supplied files, is stored using the following format:

.. code-block:: yaml

  datatree.DataTree:
    {{ detector_name }}   !!xr.Dataset
      coords:
        uts:              !!float
        mass_to_charge:   !!float                 # m/z (amu)
      data_vars:
        y:                (uts, mass_to_charge)   # Detected signal (counts)

The uncertainties in ``mass_to_charge`` are taken as the step-width of
the linearly spaced mass values.

The uncertainties in of ``y`` are the largest value between:

#. The quantization error from the ADC, its resolution assumed to be 32
   bit. Dividing F.S.R. by ``2 ** 32`` gives an error in the order of
   magnitude of the smallest data value in ``y``.
#. The contribution from neighboring masses. In the operating manual of
   the QMS 200 (see 2.8 QMS 200 F & 2.9 QMS 200 M), a maximum
   contribution from the neighboring mass of 50 ppm is noted.

.. note::

    The data in ``y`` may contain ``NaN`` s. The measured ion
    count/current value will occasionally exceed the specified detector
    F.S.R. (e.g. 1e-9), and will then flip directly to the maximum value
    of a float32. These values are set to ``float("NaN")``.

Module Functions
````````````````

"""
import datatree
from . import quadstarsac


def process(
    *,
    filetype: str,
    **kwargs: dict,
) -> datatree.DataTree:
    """
    Unified mass spectrometry data parser.Forwards ``kwargs`` to the worker functions
    based on the supplied ``filetype``.

    Parameters
    ----------
    filetype
        Discriminator used to select the appropriate worker function.

    Returns
    -------
    :class:`datatree.DataTree`

    """
    if filetype == "quadstar.sac":
        return quadstarsac.process(**kwargs)
