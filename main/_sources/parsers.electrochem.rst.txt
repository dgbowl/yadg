``electrochem``: Electrochemistry data parser
=============================================
The ``electrochem`` parser handles the reading and processing of files from
BioLogic's EC-Lab, namely the binary ``.mpr`` files and the ``.mpt``
ASCII data files.

.. note::

    This interface is not yet final and will change with version 5.0.0

``.mpt`` files are made up of a header portion (with the technique
parameter sequences and an optional loops section) and a tab-separated
data table.

``.mpr`` files are structured in a set of "modules", one concerning
settings, one for actual data, one for logs, and an optional loops
module. The parameter sequences can be found in the settings module.

The basic function of the parser is to:

#. Read in the technique data and create timesteps.
#. Collect ``metadata`` such as the measurement settings and the loops
   contained in a given file.
#. Collect ``common`` data describing the technique parameter sequences.

These are the implemented techniques for which the technique parameter
sequences can be parsed:

+------+-------------------------------------------------+
| CA   | Chronoamperometry / Chronocoulometry            |
+------+-------------------------------------------------+
| CP   | Chronopotentiometry                             |
+------+-------------------------------------------------+
| CV   | Cyclic Voltammetry                              |
+------+-------------------------------------------------+
| GCPL | Galvanostatic Cycling with Potential Limitation |
+------+-------------------------------------------------+
| GEIS | Galvano Electrochemical Impedance Spectroscopy  |
+------+-------------------------------------------------+
| LOOP | Loop                                            |
+------+-------------------------------------------------+
| LSV  | Linear Sweep Voltammetry                        |
+------+-------------------------------------------------+
| MB   | Modulo Bat                                      |
+------+-------------------------------------------------+
| OCV  | Open Circuit Voltage                            |
+------+-------------------------------------------------+
| PEIS | Potentio Electrochemical Impedance Spectroscopy |
+------+-------------------------------------------------+
| WAIT | Wait                                            |
+------+-------------------------------------------------+
| ZIR  | IR compensation (PEIS)                          |
+------+-------------------------------------------------+

Usage
-----
The use of ``electrochem`` can be specified using the ``"parser"`` keyword in
the `schema`. Further information can be specified in the
``"parameters"`` :class:`(dict)`:

- ``"filetype"`` :class:`(str)`: The file type of the raw data file.
  See :ref:`here<parsers_electrochem_formats>` for details.

.. _parsers_electrochem_provides:

Provides
--------
The ``electrochem`` parser loads all the columns present in an ``.mpt`` or
``.mpr`` file.

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


The ``"metadata"`` collected from the raw file will depend on the
``"filetype"``. For both ``.mpt`` and ``.mpr`` the ```"metadata"`` will
contain a ``"settings"`` and a ``"params"`` field:

The ``"settings"`` field for parsed ``".mpt"`` files contains the
technique name, a posix timestamp and the raw header lines as found in
the file. The ``"settings"`` from parsed ``".mpr"`` files contain the
technique and more explicitly parsed information than from ``".mpt"``
files, like the "cell characteristics" specified in EC-Lab.

The ``"params"`` will contain the technique parameter sequences and the
keys in each sequence will be the same independent of ``"filetype"`` but
an :class:`(int)`: value in the ``.mpr`` ``"params"`` may be a
:class:`(str)`: when parsed from the corresponding ``.mpt`` since the
mapping has not yet been reverse engineered.

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

    If the ``".mpr"`` file contains an ``ExtDev`` module (containing parameters
    of any external sensors plugged into the device), the ``"log"`` is usually 
    not present and therefore the full timestamp cannot be calculated.
