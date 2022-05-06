"""
The ``qftrace`` parser handles the reading and processing of the network analyzer 
traces, containing the reflection coefficient as a function of the sweeped frequency,
:math:`\\Gamma(f)`. The basic function of the parser is to:

1) read in the raw data and create timestamped `traces` 
2) detect the peaks in each trace (:math:`f_0`) and fit the quality factor :math:`Q_0`

Usage
`````
The use of :mod:`~yadg.parsers.qftrace` can be requested by supplying ``qftrace`` as
an argument to the ``parser`` keyword in the `dataschema`. The parser supports the
following parameters:

.. _yadg.parsers.qftrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_1.step.QFTrace.Params

.. _yadg.parsers.qftrace.formats:

 - LabView output in a tab-separated format (``csv``): 
   :mod:`~yadg.parsers.qftrace.labviewcsv`

.. _yadg.parsers.qftrace.provides:

Provides
````````
:mod:`~yadg.parsers.qftrace` loads the reflection trace data, determines the 
uncertainties of the signal (y-axis), and explicitly populates the points in 
the time axis (x-axis). This raw data is stored, for each
timestep, using the following format:

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


The fitting of :math:`f_0` and :math:`Q_0` to all peaks found in each trace is 
performed by :mod:`~yadg.parsers.qftrace` automatically, and can be adjusted by 
specifying the ``method`` parameter and related options. The resulting data is 
stored in the ``derived`` entry in each `timestep`, and contains the following 
information:

.. code-block:: yaml

  - derived:
      "{{ trace_name }}":   # see above, currently set to S11
        f:                  # the frequencies of each peak
          {n: [!!float, ...], s: [!!float, ...], u: "Hz"} 
        Q:                  # the cavity quality factors for each peak
          {n: [!!float, ...], s: [!!float, ...], u: "Hz"} 
          
Metadata
````````
The metadata section is currently empty.

"""
from .main import process
