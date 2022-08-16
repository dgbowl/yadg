"""
This module handles the reading and processing of X-ray photoelectron spectroscopy
data.

:mod:`~yadg.parser.xpstrace` loads X-ray photoelectron spectroscopy data, 
determines uncertainties of the signal (y-axis), and explicitly populates the 
points in the energy axis (``E``). 

Usage
`````
Available since ``yadg-4.1``. The parser supports the following parameters:

.. _yadg.parsers.xpstrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.XPSTrace.Params

.. _yadg.parsers.xpstrace.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - ULVAC PHI Multipak XPS traces (``phi.spe``),
   see :mod:`~yadg.parsers.xpstrace.phispe`

.. _yadg.parsers.xpstrace.provides:

Provides
````````
The raw data is stored, for each timestep, using the following format:

.. code-block:: yaml

    - raw:
        traces:
          "{{ trace_number }}":   # number of the trace
            name:          !!str  #
            atomic_number: !!str  #
            dwell_time:    !!str  #
            e_pass:        !!str  #
            description:   !!str  #
            E:                    # energies are always in eV
              {n: [!!float, ...], s: [!!float, ...], u: "eV"}
            y:                    # y-axis units from file
              {n: [!!float, ...], s: [!!float, ...], u: !!str}

The uncertainties ``"s"`` in ``"E"`` are taken as the step-width of
the linearly spaced energy values.

The uncertainties ``"s"`` of ``"y"`` are currently set to a constant
value of ``12.5`` counts per second as all the signals in the files seen so
far only seem to take on values in those steps.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/13

    Determining the uncertainty of the counts per second signal in XPS
    traces from the phispe parser should be done in a better way.

"""
from .main import process
