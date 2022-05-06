"""
This module handles the reading and processing of X-ray photoelectron spectroscopy
data.

Usage
`````
The usage of :mod:`~yadg.parsers.xpstrace` can be specified by supplying
``xpstrace`` as an argument to the ``parser`` keyword of the `dataschema`.
The parser supports the following parameters:

.. _yadg.parsers.xpstrace.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_1.step.XPSTrace.Params

.. _yadg.parsers.xpstrace.formats:

Formats
```````
The currently supported file formats are:

 - ULVAC PHI Multipak XPS traces (``spe``) :mod:`~yadg.parsers.xpstrace.phispe`


.. _yadg.parsers.xpstrace.provides:

Provides
````````
:mod:`~yadg.parser.xpstrace` loads X-ray photoelectron spectroscopy data, 
determines uncertainties of the signal (y-axis), and explicitly populates the 
points in the energy axis (``E``). This raw data is stored, for each timestep, 
using the following format:

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

Metadata
````````
The metadata collected from the raw files depends on the ``filetype``. The 
following metadata entries are currently stored for each `step`:

.. code-block:: yaml

    params:
      software_id:  !!str  # software name
      version:      !!str  # software version
      username:     !!str  # operator

"""
from .main import process
