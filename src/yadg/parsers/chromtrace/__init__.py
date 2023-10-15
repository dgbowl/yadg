"""
Handles the parsing of raw traces present in chromatography files, whether the source is
a liquid chromatograph (LC) or a gas chromatograph (GC). The basic function of the
parser is to:

#. read in the raw data and create timestamped `traces`
#. collect `metadata` such as the method information, sample ID, etc.

:mod:`~yadg.parsers.chromtrace` loads the chromatographic data from the specified
file, determines the uncertainties of the signal (y-axis), and explicitly
populates the points in the time axis (x-axis), when required.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.chromtrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.ChromTrace

.. _yadg.parsers.chromtrace.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - EZ-Chrom ASCII export (``ezchrom.asc``):
   see :mod:`~yadg.parsers.chromtrace.ezchromasc`
 - Agilent Chemstation Chromtab (``agilent.csv``):
   see :mod:`~yadg.parsers.chromtrace.agilentcsv`
 - Agilent OpenLab binary signal (``agilent.ch``):
   see :mod:`~yadg.parsers.chromtrace.agilentch`
 - Agilent OpenLab data archive (``agilent.dx``):
   see :mod:`~yadg.parsers.chromtrace.agilentdx`
 - Inficon Fusion JSON format (``fusion.json``):
   see :mod:`~yadg.parsers.chromtrace.fusionjson`
 - Inficon Fusion zip archive (``fusion.zip``):
   see :mod:`~yadg.parsers.chromtrace.fusionzip`

.. _yadg.parsers.chromtrace.provides:

Schema
``````
The data is returned as a :class:`datatree.DataTree`, containing a :class:`xarray.Dataset`
for each trace / detector name:

.. code-block:: yaml

  datatree.DataTree:
    {{ detector_name }}  !!xr.Dataset
      coords:
        uts:             !!float               # Timestamp of the chromatogram
        elution_time:    !!float               # The time axis of the chromatogram (s)
      data_vars:
        signal:          (uts, elution_time)   # The ordinate axis of the chromatogram

When multiple chromatograms are parsed, they are concatenated separately per detector
name. An error might occur during this concatenation if the ``elution_time`` axis changes
dimensions or coordinates between different timesteps.

.. note::

  To parse processed data in the raw data files, such as integrated peak areas or
  concentrations, use the :mod:`~yadg.parsers.chromdata` parser instead.

Module Functions
````````````````

"""

import logging
import datatree

from . import (
    ezchromasc,
    agilentcsv,
    agilentch,
    agilentdx,
    fusionjson,
    fusionzip,
)

logger = logging.getLogger(__name__)


def process(
    *,
    filetype: str,
    **kwargs: dict,
) -> datatree.DataTree:
    """
    Unified raw chromatogram parser. Forwards ``kwargs`` to the worker functions
    based on the supplied ``filetype``.

    Parameters
    ----------
    filetype
        Discriminator used to select the appropriate worker function.

    Returns
    -------
    :class:`datatree.DataTree`

    """
    if filetype == "ezchrom.asc":
        return ezchromasc.process(**kwargs)
    elif filetype == "agilent.csv":
        return agilentcsv.process(**kwargs)
    elif filetype == "agilent.dx":
        return agilentdx.process(**kwargs)
    elif filetype == "agilent.ch":
        return agilentch.process(**kwargs)
    elif filetype == "fusion.json":
        return fusionjson.process(**kwargs)
    elif filetype == "fusion.zip":
        return fusionzip.process(**kwargs)
