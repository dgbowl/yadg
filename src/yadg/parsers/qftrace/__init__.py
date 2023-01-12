"""
The module handles the reading and processing of the network analyzer
traces, containing the reflection coefficient as a function of the sweeped frequency,
:math:`\\Gamma(f)`.

:mod:`~yadg.parsers.qftrace` loads the reflection trace data, determines the
uncertainties of the signal (y-axis), and explicitly populates the points in
the time axis (x-axis).

Usage
`````
Available since ``yadg-3.0``. The parser supports the following parameters:

.. _yadg.parsers.qftrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.QFTrace.Params

.. _yadg.parsers.qftrace.formats:

 - LabView output in a tab-separated format (``csv``):
   :mod:`~yadg.parsers.qftrace.labviewcsv`

.. _yadg.parsers.qftrace.provides:

Provides
````````
This raw data is stored, for each timestep, using the following format:

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

"""
from .main import process

__all__ = ["process"]