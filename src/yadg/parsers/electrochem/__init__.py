"""
This module handles the reading and processing of files containing electrochemical
data, including BioLogic's EC-Lab file formats. The basic function of the parser is to:

#. Read in the technique data and create timesteps.
#. Collect metadata, such as the measurement settings and the loops
   contained in a given file.
#. Collect data describing the technique parameter sequences.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.electrochem.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.ElectroChem

.. _yadg.parsers.electrochem.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - EC-Lab raw data binary file and parameter settings (``eclab.mpr``),
   see :mod:`~yadg.parsers.electrochem.eclabmpr`
 - EC-Lab human-readable text export of data (``eclab.mpt``),
   see :mod:`~yadg.parsers.electrochem.eclabmpt`
 - tomato's structured json output (``tomato.json``),
   see :mod:`~yadg.parsers.electrochem.tomatojson`

Schema
``````
Depending on the filetype, the output :class:`xarray.Dataset` may contain multiple
derived values. However, all filetypes will report at least the following:

.. code-block:: yaml

  xr.Dataset:
    coords:
      uts:      !!float
    data_vars:
      Ewe:      (uts)    # Potential of the working electrode (V)
      Ece:      (uts)    # Potential of the counter electrode (V)
      I:        (uts)    # Applied current (A)

In some cases, average values (i.e. ``<Ewe>`` or ``<I>``) may be reported instead
of the instantaneous data.

.. warning::

  In previous versions of :mod:`yadg`, the :mod:`~yadg.parsers.electrochem` parser
  optionally transposed data from impedance spectroscopy, grouping the datapoints
  in each scan into a single "trace". This behaviour has been removed in ``yadg-5.0``.

Module Functions
````````````````

"""
import xarray as xr
from . import eclabmpr, eclabmpt, tomatojson


def process(
    *,
    filetype: str,
    **kwargs: dict,
) -> xr.Dataset:
    """
    Unified parser for electrochemistry data. Forwards ``kwargs`` to the worker functions
    based on the supplied ``filetype``.

    Parameters
    ----------
    filetype
        Discriminator used to select the appropriate worker function.

    Returns
    -------
    :class:`xarray.Dataset`

    """
    if filetype == "eclab.mpr":
        return eclabmpr.process(**kwargs)
    elif filetype == "eclab.mpt":
        return eclabmpt.process(**kwargs)
    elif filetype == "tomato.json":
        return tomatojson.process(**kwargs)
