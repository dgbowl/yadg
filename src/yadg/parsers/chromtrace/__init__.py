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

.. admonition:: DEPRECATED in ``yadg-4.2``

    The ``calfile``, ``detectors`` and ``species`` parameters are deprecated
    as of ``yadg-4.2`` and will stop working in ``yadg-5.0``.

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

.. admonition:: DEPRECATED in ``yadg-4.2``

  The below functionality has been deprecated in ``yadg-4.2`` and will stop working
  in ``yadg-5.0``.

The data processing performed by :mod:`~yadg.parsers.chromtrace` is enabled 
automatically when calibration information is provided. The resulting data is stored 
in the ``derived`` entry in each `timestep`, and contains the following information:

.. code-block:: yaml

  - derived:
      peaks:
        "{{ trace_name }}":     # detector name from raw data file
          "{{ species_name }}": # species name matched from calibration
            peak:
              max:      !!int   # index of peak maximum
              llim:     !!int   # index of peak left limit
              rlim:     !!int   # index of peak right limit
            A:                  # integrated peak area 
              {n: !!float, s: !!float, u: !!str} 
            h:                  # height of peak maximum
              {n: !!float, s: !!float, u: !!str} 
            c:                  # calibrated "concentration" or other quantity
              {n: !!float, s: !!float, u: !!str} 
      height:                   # baseline-corrected height of peak maximum
        "{{ species_name }}":
            {n: !!float, s: !!float, u: !!str}
      area:                     # integrated area of the sample peak
        "{{ species_name }}":
            {n: !!float, s: !!float, u: !!str}
      concentration:            # concentration of species derived from area
        "{{ species_name }}":
            {n: !!float, s: !!float, u: !!str}
      xout:                     # normalised mol fractions of species
        "{{ species_name }}":
            {n: !!float, s: !!float, u: !!str}

.. note::

    The specification of dictionaries that ought to be passed to ``species`` and 
    ``detectors`` (or stored as json in ``"calfile"``) is described in 
    :func:`yadg.parsers.chromtrace.main.parse_detector_spec`. 

.. note::

    The quantity ``c``, determined for each integrated peak, may not necessarily 
    be concentration. It can also be mole fraction, as it is determined from the 
    peak area in ``A`` and any provided calibration specification. The calibration 
    interface allows for units to be supplied.

.. note::

    The mol fractions in ``xout`` always sum up to unity. If there is more than
    one outlet stream, these mol fractions have to be weighted by the flow rate 
    in a post-processing routine.

"""
from .main import process
