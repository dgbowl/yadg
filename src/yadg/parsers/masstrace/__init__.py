"""
The module handles the reading and processing of mass spectrometry files. The 
basic function of the parser is to:

#. read in the raw data and create timestamped ``traces``
#. collect `metadata` such as the software version, author, etc.

Usage
`````
Select :mod:`~yadg.parsers.masstrace` by supplying it to the ``parser`` keyword 
in the `dataschema`. The parser supports the following parameters:

.. _yadg.parsers.masstrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.MassTrace.Params

.. _yadg.parsers.masstrace.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - Pfeiffer Quadstar 32-bit scan analog data (``quadstar.sac``),
   see :mod:`~yadg.parsers.masstrace.quadstarsac`
 
.. _yadg.parsers.masstrace.provides:

Provides
````````
The raw data, loaded from the supplied files, is stored using the following format:

.. code-block:: yaml

    - raw:
        traces:
          "{{ trace_number }}":  # number of the trace
            y_title: !!str       # y-axis label from file
            comment: !!str       # comment
            fsr:     !!str       # full scale range of the detector
            m/z:                 # masses are always in amu
              {n: [!!float, ...], s: [!!float, ...], u: "amu"}
            y:                   # y-axis units from file
              {n: [!!float, ...], s: [!!float, ...], u: !!str}

The uncertainties ``"s"`` in ``m/z`` are taken as the step-width of
the linearly spaced mass values.

The uncertainties ``"s"`` of ``y`` are the largest value between:

#. The quantization error from the ADC, its resolution assumed to be 32
   bit. Dividing F.S.R. by ``2 ** 32`` gives an error in the order of
   magnitude of the smallest data value in ``y``.
#. The contribution from neighboring masses. In the operating manual of
   the QMS 200 (see 2.8 QMS 200 F & 2.9 QMS 200 M), a maximum
   contribution from the neighboring mass of 50 ppm is noted.

.. note::

    The data in ``y`` may contain ``NaN`` s. The measured ion
    count/current value will occasionally exceed the specified detector
    F.S.R. (e.g. 1e-9), and will then flip directly to the maximum value
    of a float32. These values are set to ``float("NaN")``.
 
"""
from .main import process
