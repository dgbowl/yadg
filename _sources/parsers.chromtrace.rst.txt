``chromtrace``: Chromatogram parser
===================================
The ``chromtrace`` parser handles the reading and processing of all chromatography 
files, whether the source is a liquid chromatograph (LC) or a gas chromatograph (GC). 
The basic function of the parser is to:

1) read in the raw data and create timestamped `traces`
2) collect `metadata` such as the method information, sample ID, etc.
3) match and integrate peaks in each `trace` using built-in routines
4) calculate the outlet composition ``xout`` if calibration information is provided

Points 1), 2) and 4) are discussed in the :ref:`Provides<parsers_chromtrace_provides>`
section below. Point 3) is described in the documentation of the 
:ref:`integration module<parsers_chromtrace_integration>`.

Usage
-----
The use of ``chromtrace`` can be specified using the ``"parser"`` keyword in the
`schema`. Further information can be specified in the ``"parameters"`` :class:`(dict)`:

- ``"tracetype"`` :class:`(str)`: The file type of the raw data file. 
  See :ref:`here<parsers_chromtrace_formats>` for details.
- ``"calfile"`` :class:`(str)`: The calibration file in a json format.
- ``"detectors"`` :class:`(dict)`: The detector specification, overriding that
  provided in ``"calfile"``. 
- ``"species"`` :class:`(dict)`: The species data specification, overriding that
  provided in ``"calfile"``. 

.. note::
    The ``"calfile"``, ``"detectors"`` and ``"species"`` parameters are processed with
    :func:`yadg.parsers.chromtrace.main.parse_detector_spec` - see there for detailed
    format description.

.. _parsers_chromtrace_provides:

Provides
--------
The primary functionality of ``chromtrace`` is to load the chromatographic data, 
including determining uncertainties of the signal (y-axis), as well as explicitly 
populating the points in the time axis (x-axis). This raw data is stored, for each
timestep, in the ``"raw"`` entry using the following format:

.. code-block:: yaml

  - raw:
      traces:
        "{{ trace_name }}":        # detector name from the raw data file
          id:               !!int  # detector id for matching with calibration data
          t:                       # time-axis units are always seconds
            {n: [!!float, ...], s: [!!float, ...], u: "s"} 
          y:                       # y-axis units are determined from raw file
            {n: [!!float, ...], s: [!!float, ...], u: !!str}  
            
        
The ``"metadata"`` collected from the raw file varies greatly by the raw file format. 
See :ref:`here<parsers_chromtrace_formats>` for details. In general, the following
metadata entries are stored in the ``"params"`` element of each `step`:

.. code-block:: yaml
  
  params:
    method:   !!str # path or other specifier of the chromatographic method
    sampleid: !!str # sample ID
    username: !!str # username of raw file creator
    version:  !!str # raw file version or program version
    valve:    !!int # multiplexer valve number
    datafile: !!str # original data file location

The data processing performed in ``chromtrace`` is enabled automatically when
calibration information are provided. The resulting data is stored in the 
``"derived"`` entry in each `timestep`, and contains the following information:

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
      xout:                     # normalised mol fractions of species
        "{{ species_name }}":
            {n: !!float, s: !!float, u: !!str}

.. note::
    The specification of dictionaries that ought to be passed to ``"species"`` and 
    ``"detectors"`` (or stored as json in ``"calfile"``) is described in 
    :func:`yadg.parsers.chromtrace.main.parse_detector_spec`. 

.. note::
    The quantity in ``"c"`` may not necessarily be concentration, it can also be 
    mole fraction, as it is determined from the peak area in ``"A"`` and any 
    provided calibration specification. The calibration interface allows for units
    to be supplied.

.. note::
    The mol fractions in ``"xout"`` always sum up to unity. If there is more than
    one outlet stream, these mol fractions have to be weighted by the flow rate 
    in a post-processing routine.

      
