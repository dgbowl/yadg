"""
This module handles the reading and processing of files containing electrochemical
data, including BioLogic's EC-Lab file formats.

.. note::

    This interface is not yet final and will change with version 5.0.0

Usage
`````
The usage of :mod:`~yadg.parsers.electrochem` can be specified by supplying
``electrochem`` as an argument to the ``parser`` keyword of the `dataschema`.
The parser supports the following parameters:

.. _yadg.parsers.electrochem.model:

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_4_1.step.ElectroChem.Params

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

For impedance spectroscopy techniques (PEIS, GEIS), the data is made up
of spectroscopy traces. The data is thus split into traces by the column
``"cycle number"`` and each trace is cast into a single timestep. Each trace 
now corresponds to a spectroscopy scan, indexed by the technique name (PEIS or
GEIS). The timestep takes the following format:

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

    The parsed data may contain infinities (i.e. ``float("inf")`` /
    ``float("-inf")``) or NaNs (i.e. ``float("nan")``). While datagrams 
    containing NaN and Inf can be exported and read back using python's json 
    module, they are not strictly valid jsons.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/10

    Current values of the uncertainties ``"s"`` are hard-coded from VMP-3 values
    of resolutions and accuracies, with ``math.ulp(n)`` as fallback. The values 
    should be device-specific, and the fallback should be eliminated.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/11

    The "raw" data in electrochemistry files should only contain the raw quantities,
    that is the ``control_I`` or ``control_V`` and the measured potentials ``Ewe``,
    ``Ece`` or the measured current ``I``. Analogous quantities should be recorded
    for PEIS/GEIS. All other columns should be computed by **yadg**.

Metadata
````````
The metadata collected from the raw file will depend on the ``filetype``. Currently,
no metadata is recorded for ``tomato.json`` filetype. For the ``eclab.mpt`` and 
``eclab.mpr`` filetypes, the metadata will contain a ``settings`` and a ``params`` 
field:

The ``settings`` field for parsed ``.mpt`` files contains the technique name, a 
posix timestamp and the raw header lines as found in the file. The ``settings`` 
from parsed ``.mpr`` files contain the technique and more explicitly parsed 
information than from ``.mpt`` files, like the "cell characteristics" specified 
in EC-Lab.

The ``params`` will contain the technique parameter sequences and the
keys in each sequence will be the same independent of ``filetype``, but
an :class:`int` value in the ``.mpr`` file may be a :class:`str` when 
parsed from the corresponding ``.mpt`` file, since the mapping has not 
yet been reverse engineered.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/12

    In ``.mpr`` files, some technique parameters in the settings module
    correspond to entries in drop-down lists in EC-Lab. These values are
    stored as single-byte values in ``.mpr`` files.

The metadata from parsed ``".mpr"`` files also provides the ``"log"``
which contains more general parameters, like software, firmware and
server versions, channel number, host address and an acquisition start
timestamp in Microsoft OLE format. 

.. note::

    If the ``.mpr`` file contains an ``ExtDev`` module (containing parameters
    of any external sensors plugged into the device), the ``log`` is usually 
    not present and therefore the full timestamp cannot be calculated.

"""
from .main import process
