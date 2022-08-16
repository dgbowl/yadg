"""
This module handles the reading and processing of X-ray diffraction data.

:mod:`~yadg.parsers.xrdtrace` loads X-ray diffraction data, determines reasonable 
uncertainties of the signal intensity (y-axis), and explicitly populates the angle
axis (:math:`2\\theta`), if necessary. 

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.xrdtrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.XRDTrace.Params

.. _yadg.parsers.xrdtrace.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - PANalytical ``xrdml`` files (``panalytical.xrdml``),
   see :mod:`~yadg.parsers.xrdtrace.panalyticalxrdml`
 - PANalytical ``csv`` files (``panalytical.csv``),
   see :mod:`~yadg.parsers.xrdtrace.panalyticalcsv`
 - PANalytical ``xy`` files (``panalytical.xy``),
   see :mod:`~yadg.parsers.xrdtrace.panalyticalxy`

.. _yadg.parsers.xrdtrace.provides:

Provides
````````
The raw data is stored, for each timestep, using the following format:

.. code-block:: yaml

    - raw:
        traces:
          "{{ trace_number }}":   # number of the trace
            angle:                
              {n: [!!float, ...], s: [!!float, ...], u: "deg"}
            intensity:
              {n: [!!float, ...], s: [!!float, ...], u: "counts"}

The uncertainties ``"s"`` in ``"angle"`` are taken as the step-width of
the linearly spaced :math:`2\\theta` values.

The uncertainties ``"s"`` of ``"intensity"`` are currently set to a constant
value of 1.0 count as all the supported files seem to produce integer values.


"""
from .main import process
