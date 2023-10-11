"""
Handles the reading of post-processed chromatography data, i.e. files containing peak
areas, concentrations, or mole fractions.

.. note::

  To parse trace data as present in raw chromatograms, use the
  :mod:`~yadg.parsers.chromtrace` parser.

Usage
`````
Available since ``yadg-4.2``. The parser supports the following parameters:

.. _yadg.parsers.chromdata.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_0.step.ChromData

.. _yadg.parsers.chromdata.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - Inficon Fusion JSON format (``fusion.json``):
   see :mod:`~yadg.parsers.chromdata.fusionjson`
 - Inficon Fusion zip archive (``fusion.zip``):
   see :mod:`~yadg.parsers.chromdata.fusionzip`
 - Inficon Fusion csv export (``fusion.csv``):
   see :mod:`~yadg.parsers.chromdata.fusioncsv`
 - Empa's Agilent LC csv export (``empalc.csv``):
   see :mod:`~yadg.parsers.chromdata.empalccsv`
 - Empa's Agilent LC excel export (``empalc.xlsx``):
   see :mod:`~yadg.parsers.chromdata.empalcxlsx`

Schema
``````
Each file is processed into a single :class:`xarray.Dataset`, containing the following
``coords`` and ``data_vars`` (if present in the file):

.. code-block:: yaml

  xr.Dataset:
    coords:
      uts:            !!float               # Unix timestamp
      species:        !!str                 # Species names
    data_vars:
      height:         (uts, species)        # Peak height maximum
      area:           (uts, species)        # Integrated peak area
      retention time: (uts, species)        # Peak retention time
      concentration:  (uts, species)        # Species concentration (mol/l)
      xout:           (uts, species)        # Species mole fraction (-)

Module Functions
````````````````

"""
import xarray as xr

from . import (
    fusionjson,
    fusionzip,
    fusioncsv,
    empalccsv,
    empalcxlsx,
)


def process(*, filetype: str, **kwargs: dict) -> xr.Dataset:
    """
    Unified chromatographic data parser. Forwards ``kwargs`` to the worker functions
    based on the supplied ``filetype``.

    Parameters
    ----------
    filetype
        Discriminator used to select the appropriate worker function.

    Returns
    -------
    :class:`xarray.Dataset`

    """
    if filetype == "fusion.json":
        return fusionjson.process(**kwargs)
    elif filetype == "fusion.zip":
        return fusionzip.process(**kwargs)
    elif filetype == "fusion.csv":
        return fusioncsv.process(**kwargs)
    elif filetype == "empalc.csv":
        return empalccsv.process(**kwargs)
    elif filetype == "empalc.xlsx":
        return empalcxlsx.process(**kwargs)
