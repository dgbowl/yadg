"""
This module handles the reading and processing of X-ray diffraction data.

Usage
`````
The usage of :mod:`~yadg.parsers.xrdtrace` can be specified by supplying 
``xrdtrace`` as an argument to the ``parser`` keyword of the `dataschema`. 
The parser supports the following parameters:

.. _yadg.parsers.xrdtrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_1.step.XRDTrace.Params

.. _yadg.parsers.xrdtrace.formats:

Formats
```````
The currently supported file formats are:

 - PANalytical ``xrdml`` files: :mod:`~yadg.parsers.xrdtrace.panalyticalxrdml`
 - PANalytical ``csv`` files: :mod:`~yadg.parsers.xrdtrace.panalyticalcsv`
 - PANalytical ``xy`` files: :mod:`~yadg.parsers.xrdtrace.panalyticalxy`

.. _yadg.parsers.xrdtrace.provides:

Provides
````````
:mod:`~yadg.parsers.xrdtrace` loads X-ray diffraction data, determines reasonable 
uncertainties of the signal intensity (y-axis), and explicitly populates the angle
axis (:math:`2\\theta`), if necessary. This raw data is stored, for each timestep, 
using the following format:

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

Metadata
````````
.. warning::
  
  The metadata collected from the raw data file depends on the filetype, and 
  is currently not strictly defined.

"""
from .main import process
