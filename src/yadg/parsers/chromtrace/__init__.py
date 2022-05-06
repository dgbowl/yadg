"""
The ``chromtrace`` parser handles the reading and processing of all chromatography 
files, whether the source is a liquid chromatograph (LC) or a gas chromatograph (GC). 
The basic function of the parser is to:

1) read in the raw data and create timestamped `traces`
2) collect `metadata` such as the method information, sample ID, etc.
3) match and integrate peaks in each `trace` using built-in routines
4) calculate the outlet composition ``xout`` if calibration information is provided

Usage
`````
The use of :mod:`~yadg.parsers.chromtrace` can be requested by supplying ``chromtrace``
as an argument to the ``parser`` keyword of the `dataschema`. The parser supports the
following parameters:

.. _yadg.parsers.chromtrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_1.step.ChromTrace.Params

.. note::

    The ``calfile``, ``detectors`` and ``species`` parameters are processed with
    :func:`~yadg.parsers.chromtrace.main.parse_detector_spec`. See there for a 
    detailed format description.

.. _yadg.parsers.chromtrace.formats:

Formats
```````
The formats currently supported by the parser are:

 - EZ-Chrom ASCII export (``dat.asc``): :mod:`~yadg.parsers.chromtrace.ezchromasc`
 - Agilent Chemstation Chromtab (``csv``): :mod:`~yadg.parsers.chromtrace.agilentcsv`
 - Agilent OpenLab binary signal (``ch``): :mod:`~yadg.parsers.chromtrace.agilentch`
 - Agilent OpenLab data archive (``dx``): :mod:`~yadg.parsers.chromtrace.agilentdx`
 - Inficon Fusion JSON format (``json``): :mod:`~yadg.parsers.chromtrace.fusionjson`
 - Inficon Fusion zip archive (``zip``) :mod:`~yadg.parsers.chromtrace.fusionzip`

.. _yadg.parsers.chromtrace.provides:

Provides
````````
:mod:`~yadg.parsers.chromtrace`` loads the chromatographic data from the specified
file, determines the uncertainties of the signal (y-axis), and explicitly 
populates the points in the time axis (x-axis), when required. This raw data is 
stored, for each timestep, using the following format:

.. code-block:: yaml

  - raw:
      traces:
        "{{ trace_name }}":        # detector name from the raw data file
          id:               !!int  # detector id for matching with calibration data
          t:                       # time-axis units are always seconds
            {n: [!!float, ...], s: [!!float, ...], u: "s"} 
          y:                       # y-axis units are determined from raw file
            {n: [!!float, ...], s: [!!float, ...], u: !!str}  

If the raw data file contains information such as peak areas, concentrations, or mol
fractions for detected species those are also included in the timestep:

.. code-block:: yaml

  raw:
    height:                     # height of the peak maxima
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    area:                       # integrated area of the peak
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    concentration:              # concentration
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: !!str}
    xout:                       # normalised concentration
      "{{ species_name }}": 
          {n: !!float, s: !!float, u: " "}

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

Metadata
````````
The metadata collected from the raw file varies greatly by the raw file format. 
See the documentation of each file parser for details. In general, the following
metadata entries are stored for each `step`:

.. code-block:: yaml
  
  params:
    method:   !!str # path or other specifier of the chromatographic method
    sampleid: !!str # sample ID
    username: !!str # username of raw file creator
    version:  !!str # raw file version or program version
    valve:    !!int # multiplexer valve number
    datafile: !!str # original data file location


"""
from .main import process
