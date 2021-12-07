``qftrace``: VNA trace parser
=============================
The ``qftrace`` parser handles the reading and processing of the network analyzer 
traces, containing the reflection coefficient as a function of the sweeped frequency,
:math:`\Gamma(f)`. The basic function of the parser is to:

1) read in the raw data and create timestamped `traces` 
2) detect the peaks in each trace (:math:`f_0`) and fit the quality factor :math:`Q_0`

Usage
-----
The use of ``qftrace`` can be specified using the ``"parser"`` keyword in the
`schema`. Further information can be specified in the ``"parameters"`` :class:`(dict)`:

- ``"tracetype"`` :class:`(str)`: The file type of the raw data file. 
  See :ref:`here<parsers_qftrace_formats>` for details.
- ``"method"`` :class:`(str)`: The fitting routine to be used to obtain :math:`Q_0`.
  See :ref:`here<parsers_qftrace_methods>` for a list of available methods.
- ``"cutoff"`` :class:`(float)`: The cutoff controlling the height-based pruning.
  See :func:`yadg.parsers.qftrace.prune.cutoff`.
- ``"threshold"`` :class:`(float)`: The threshold controlling gradient-based pruning.
  See :func:`yadg.parsers.qftrace.prune.gradient`.
- ``"height"`` :class:`(float)`: Peak-picking parameter, determining the relative 
  peak height of a peak. 
- ``"distance"`` :class:`(float)`: Peak-picking parameter, determining the minimum 
  distance between two peaks. 


.. _parsers_qftrace_provides:

Provides
--------
The primary functionality of ``qfromtrace`` is to load the chromatographic data, 
including determining uncertainties of the signal (y-axis), as well as explicitly 
populating the points in the time axis (x-axis). This raw data is stored, for each
timestep, in the ``"raw"`` entry using the following format:

.. code-block:: yaml

  - raw:
      avg:             !!int  # number of scans that are averaged for each trace
      bw:                     # filter bandwith used to measure the trace
        {n: !!float, s: !!float, u: "Hz"}
      traces:
        "{{ trace_name }}":   # detector name, currently hard-coded to S11
          f:                  # frequency-axis units are always Hz
            {n: [!!float, ...], s: [!!float, ...], u: "Hz"} 
          Re(Γ):              # real part of the reflection coefficient
            {n: [!!float, ...], s: [!!float, ...], u: !!str}  
          Im(Γ):              # imaginary part of the reflection coefficient
            {n: [!!float, ...], s: [!!float, ...], u: !!str}  
      
        
The ``"metadata"`` section is currently empty.

The fitting of :math:`f_0` and :math:`Q_0` to all peaks found in each trace is 
performed by ``qftrace`` automatically, and can be adjusted by specifying the 
``"method"`` parameter and related options.  The resulting data is stored in the 
``"derived"`` entry in each `timestep`, and contains the following information:

.. code-block:: yaml

  - derived:
      "{{ trace_name }}":   # see above, currently set to S11
        f:                  # the frequencies of each peak
          {n: [!!float, ...], s: [!!float, ...], u: "Hz"} 
        Q:                  # the cavity quality factors for each peak
          {n: [!!float, ...], s: [!!float, ...], u: "Hz"} 
          



      
