"""
This module handles the reading and processing of files containing electrochemical
data, including BioLogic's EC-Lab file formats. The basic function of the parser is to:

#. Read in the technique data and create timesteps.
#. Collect metadata, such as the measurement settings and the loops
   contained in a given file.
#. Collect data describing the technique parameter sequences.

Usage
`````
Available since ``yadg-4.0``. The parser supports the following parameters:

.. _yadg.parsers.electrochem.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_2.step.ElectroChem.Params

.. _yadg.parsers.electrochem.formats:

Formats
```````
The ``filetypes`` currently supported by the parser are:

 - EC-Lab raw data binary file and parameter settings (``eclab.mpr``),
   see :mod:`~yadg.parsers.electrochem.eclabmpr`
 - EC-Lab human-readable text export of data (``eclab.mpt``),
   see :mod:`~yadg.parsers.electrochem.eclabmpt`
 - tomato's structured json output (``tomato.json``),
   see :mod:`~yadg.parsers.electrochem.tomatojson`
  
Provides
````````
Most standard techniques write data that can be understood as a series of
timesteps, with a measurement of the potential of the working electrode ``Ewe``,
the current applied by the potentiostat ``I``, and if present, also the potential
of the counter electrode ``Ece``. Depending on the technique, these quantitites
may be recorded as averages, i.e. ``<Ewe>``, ``<Ece>``, and ``<I>``. Technique 
metadata, such as the ``cycle number`` and the name of the ``technique`` are also
stored in each timestep:

.. code-block:: yaml

    - fn   !!str
      uts  !!float
      raw:
        Ewe:                 # potential of the working electrode, might be <Ewe>
          {n: !!float, s: !!float, u: !!str}
        Ece:                 # potential of the counter electrode, might be <Ece>
          {n: !!float, s: !!float, u: !!str}
        I:                   # current, might be <I>
          {n: !!float, s: !!float, u: !!str}
        cycle number: !!int
        technique:    !!str 

For impedance spectroscopy techniques (PEIS, GEIS), the data is by default
transposed to be made of spectroscopy traces. The data is split into traces using 
the ``cycle number`` column, and each trace is cast into a single timestep. Each 
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

.. note::

  This transposing behaviour can be toggled off by setting the ``transpose`` 
  parameter to ``False``, see documentation of the 
  :class:`~dgbowl_schemas.yadg.dataschema_4_2.step.ElectroChem.Params` class.


"""
from .main import process
