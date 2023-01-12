"""
This module handles the parsing of raw traces present in chromatography files,
whether the source is a liquid chromatograph (LC) or a gas chromatograph (GC).
The basic function of the parser is to:

#. read in the raw data and create timestamped `traces`
#. collect `metadata` such as the method information, sample ID, etc.

:mod:`~yadg.parsers.chromtrace` loads the chromatographic data from the specified
file, determines the uncertainties of the signal (y-axis), and explicitly
populates the points in the time axis (x-axis), when required.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.chromtrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.ChromTrace.Params

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

Provides
````````
The raw data is stored, for each timestep, using the following format:

.. code-block:: yaml

  - uts: !!float
    fn:  !!str
    raw:
      traces:
        "{{ trace_name }}":        # detector name from the raw data file
          id:               !!int  # detector id for matching with calibration data
          t:                       # time-axis units are always seconds
            {n: [!!float, ...], s: [!!float, ...], u: "s"}
          y:                       # y-axis units are determined from raw file
            {n: [!!float, ...], s: [!!float, ...], u: !!str}

.. note::

  To parse processed data in the raw data files, such as integrated peak areas or
  concentrations, use the :mod:`~yadg.parsers.chromdata` parser instead.

"""
from .main import process

__all__ = ["process"]
