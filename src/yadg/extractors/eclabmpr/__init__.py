"""
**eclabmpr**: Processing of BioLogic's EC-Lab binary modular files.
-------------------------------------------------------------------

``.mpr`` files are structured in a set of "modules", one concerning
settings, one for actual data, one for logs, and an optional loops
module. The parameter sequences can be found in the settings module.

This code is partly an adaptation of the `galvani module by Chris
Kerr <https://github.com/echemdata/galvani>`_, and builds on the work done
by the previous civilian service member working on the project, Jonas Krieger.

.. _yadg.parsers.electrochem.eclabmpr.techniques:

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

.. note::

    ``.mpt`` files can contain more data than the corresponding binary
    ``.mpr`` file.

File Structure of ``.mpr`` Files
````````````````````````````````

At a top level, ``.mpr`` files are made up of a number of modules,
separated by the ``MODULE`` keyword. In all the files I have seen, the
first module is the settings module, followed by the data module, the
log module and then an optional loop module.

.. code-block::

    0x0000 BIO-LOGIC MODULAR FILE  # File magic.
    0x0034 MODULE                  # Module magic.
    ...                            # Module 1.
    0x???? MODULE                  # Module magic.
    ...                            # Module 2.
    0x???? MODULE                  # Module magic.
    ...                            # Module 3.
    0x???? MODULE                  # Module magic.
    ...                            # Module 4.

After splitting the entire file on ``MODULE``, each module starts with a
header that is structured like this (offsets from start of module):

.. code-block::

    0x0000 short_name  # Short name, e.g. VMP Set.
    0x000A long_name   # Longer name, e.g. VMP settings.
    0x0023 length      # Number of bytes in module data.
    0x0027 version     # Module version.
    0x002B date        # Acquisition date in ASCII, e.g. 08/10/21.
    ...                # Module data.

The contents of each module's data vary wildly depending on the used
technique, the module and perhaps the software version, the settings in
EC-Lab, etc. Here a quick overview (offsets from start of module data).

*Settings Module*

.. code-block::

    0x0000 technique_id           # Unique technique ID.
    ...                           # ???
    0x0007 comments               # Pascal string.
    ...                           # Zero padding.
    # Cell Characteristics.
    0x0107 active_material_mass   # Mass of active material
    0x010B at_x                   # at x =
    0x010F molecular_weight       # Molecular weight of active material
    0x0113 atomic_weight          # Atomic weight of intercalated ion
    0x0117 acquisition_start      # Acquisition started a: xo =
    0x011B e_transferred          # Number of e- transferred
    0x011E electrode_material     # Pascal string.
    ...                           # Zero Padding
    0x01C0 electrolyte            # Pascal string.
    ...                           # Zero Padding, ???.
    0x0211 electrode_area         # Electrode surface area
    0x0215 reference_electrode    # Pascal string
    ...                           # Zero padding
    0x024C characteristic_mass    # Characteristic mass
    ...                           # ???
    0x025C battery_capacity       # Battery capacity C =
    0x0260 battery_capacity_unit  # Unit of the battery capacity.
    ...                           # ???
    # Technique parameters can randomly be found at 0x0572, 0x1845 or
    # 0x1846. All you can do is guess and try until it fits.
    0x1845 ns                     # Number of sequences.
    0x1847 n_params               # Number of technique parameters.
    0x1849 params                 # ns sets of n_params parameters.
    ...                           # ???

*Data Module*

.. code-block::

    0x0000 n_datapoints  # Number of datapoints.
    0x0004 n_columns     # Number of values per datapoint.
    0x0005 column_ids    # n_columns unique column IDs.
    ...
    # Depending on module version, datapoints start 0x0195 or 0x0196.
    # Length of each datapoint depends on number and IDs of columns.
    0x0195 datapoints    # n_datapoints points of data.

*Log Module*

.. code-block::

    ...                         # ???
    0x0009 channel_number       # Zero-based channel number.
    ...                         # ???
    0x00AB channel_sn           # Channel serial number.
    ...                         # ???
    0x01F8 Ewe_ctrl_min         # Ewe ctrl range min.
    0x01FC Ewe_ctrl_max         # Ewe ctrl range max.
    ...                         # ???
    0x0249 ole_timestamp        # Timestamp in OLE format.
    0x0251 filename             # Pascal String.
    ...                         # Zero padding, ???.
    0x0351 host                 # IP address of host, Pascal string.
    ...                         # Zero padding.
    0x0384 address              # IP address / COM port of potentiostat.
    ...                         # Zero padding.
    0x03B7 ec_lab_version       # EC-Lab version (software)
    ...                         # Zero padding.
    0x03BE server_version       # Internet server version (firmware)
    ...                         # Zero padding.
    0x03C5 interpreter_version  # Command interpretor version (firmware)
    ...                         # Zero padding.
    0x03CF device_sn            # Device serial number.
    ...                         # Zero padding.
    0x0922 averaging_points     # Smooth data on ... points.
    ...                         # ???

*Loop Module*

.. code-block::

    0x0000 n_indexes  # Number of loop indexes.
    0x0004 indexes    # n_indexes indexes at which loops start in data.
    ...               # ???


Metadata
````````
The metadata will contain the information from the *Settings module*. This should
include information about the technique, as well as any explicitly parsed cell
characteristics data specified in EC-Lab.

.. admonition:: TODO

    https://github.com/dgbowl/yadg/issues/12

    The mapping between metadata parameters between ``.mpr`` and ``.mpt`` files
    is not yet complete. In ``.mpr`` files, some technique parameters in the settings
    module correspond to entries in drop-down lists in EC-Lab. These values are
    stored as single-byte values in ``.mpr`` files.

The metadata also contains the infromation from the *Log module*, which contains
more general parameters, like software, firmware and server versions, channel number,
host address and an acquisition start timestamp in Microsoft OLE format.

.. note::

    If the ``.mpr`` file contains an ``ExtDev`` module (containing parameters
    of any external sensors plugged into the device), the ``log`` is usually
    not present and therefore the full timestamp cannot be calculated.

.. codeauthor:: Nicolas Vetsch
"""
from zoneinfo import ZoneInfo
from pathlib import Path
from dgbowl_schemas.yadg import FileType
import logging
import pandas as pd
from .extractor import process

logger = logging.getLogger(__name__)

supports = {
    "eclab.mpr",
    "marda:biologic-mpr",
}


def extract(
    path: Path,
    filetype: FileType,
) -> tuple[dict, pd.DataFrame, pd.DataFrame, dict]:

    metadata, nominal, sigma, units = process(
        fn=str(path),
        timezone=ZoneInfo(filetype.timezone),
    )

    return metadata, nominal, sigma, units
