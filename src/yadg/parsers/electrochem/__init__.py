"""
This module handles the reading and processing of files containing electrochemical
data, including BioLogic's EC-Lab file formats.

Usage
`````
Select :mod:`~yadg.parsers.electrochem` by supplying ``electrochem`` to the 
``parser`` keyword, starting in :class:`DataSchema-4.0`. The parser supports the 
following parameters:

.. _yadg.parsers.electrochem.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.ElectroChem.Params

.. _yadg.parsers.electrochem.formats:

Formats
```````
The currently supported file formats are:

 - EC-Lab raw data binary file and parameter settings
   :mod:`~yadg.parsers.electrochem.eclabmpr`
 - EC-Lab human-readable text export of data
   :mod:`~yadg.parsers.electrochem.eclabmpt`
 - tomato's structured json output
   :mod:`~yadg.parsers.electrochem.tomatojson`
  
Provides
````````
The basic function of the parser is to:

#. Read in the technique data and create timesteps.
#. Collect metadata, such as the measurement settings and the loops
   contained in a given file.
#. Collect data describing the technique parameter sequences.

.. note::

    ``.mpt`` files can contain more data than the corresponding binary
    ``.mpr`` file.

Most techniques write data that can be understood as a series of
timesteps. Each timestep provided by the parser has the following
format:

.. code-block:: yaml

    - fn   !!str
    - uts  !!float
    - raw:
        "{{ col1 }}":  !!int
        "{{ col2 }}":
          {n: !!float, s: !!float, u: !!str}

For impedance spectroscopy techniques (PEIS, GEIS), the data is by default
transposed to be made of spectroscopy traces. The data is split into traces using 
the ``"cycle number"`` column, and each trace is cast into a single timestep. Each 
trace now corresponds to a spectroscopy scan, indexed by the technique name (PEIS 
or GEIS). The timestep takes the following format:

.. code-block:: yaml

    - fn   !!str
    - uts  !!float
    - raw:
        traces:
          "{{ technique }}":
            "{{ col1 }}":
                [!!int, ...]
            "{{ col2 }}":
                {n: [!!float, ...], s: [!!float, ...], u: !!str}

This behaviour can be toggled off by setting the ``transpose`` parameter to ``False``,
see :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.ElectroChem.Params`.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/10

    Current values of the uncertainties ``"s"`` are hard-coded from VMP-3 values
    of resolutions and accuracies, with ``math.ulp(n)`` as fallback. The values 
    should be device-specific, and the fallback should be eliminated.


"""
from .main import process
