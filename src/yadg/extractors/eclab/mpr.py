"""
For processing of BioLogic's EC-Lab binary modular files.

Usage
`````
Available since ``yadg-4.0``.

.. autopydantic_model:: dgbowl_schemas.yadg.dataschema_5_1.filetype.EClab_mpr

Schema
``````
The ``mpr`` files contain many columns that vary depending on the electrochemical
technique used. Below is shown a list of columns that can be expected to be present
in a typical ``mpr`` file.

.. code-block:: yaml

    datatree.DataTree:
      coords:
        uts:            !!float     # Unix timestamp, without date
      data_vars:
        Ewe             (uts)       # Potential of the working electrode
        Ece             (uts)       # Potential of the counter electrode, if present
        I               (uts)       # Instantaneous current
        time            (uts)       # Time elapsed since the start of the experiment
        <Ewe>           (uts)       # Average Ewe potential since last data point
        <Ece>           (uts)       # Average Ece potential since last data point
        <I>             (uts)       # Average current since last data point
        ...

.. note::

     Note that in most cases, either the instantaneous or the averaged quantities are
     stored - only rarely are both available!

Notes on file structure
```````````````````````
``.mpr`` files are structured in a set of "modules", one concerning
settings, one for actual data, one for logs, and an optional loops
module. The parameter sequences can be found in the settings module.

This code is partly an adaptation of the `galvani module by Chris
Kerr <https://github.com/echemdata/galvani>`_, and builds on the work done
by the previous civilian service member working on the project, Jonas Krieger.

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

    0x0000 n_datapoints   # Number of datapoints.
    0x0004 n_columns      # Number of values per datapoint.
    0x0005 column_ids     # n_columns unique column IDs.
    ...
    # Depending on module version, datapoints start 0x195, 0x196, or 0x3ef
    # Length of each datapoint depends on number and IDs of columns.
    0x0195 datapoints     # n_datapoints points of data.

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

.. codeauthor::
    Nicolas Vetsch

"""

import logging
from datatree import DataTree
import numpy as np
from yadg import dgutils
from .techniques import (
    technique_params_dtypes,
    param_from_key,
    get_devs,
)
from .mpr_columns import (
    module_header_dtypes,
    settings_dtypes,
    flag_columns,
    data_columns,
    log_dtypes,
    extdev_dtypes,
)

logger = logging.getLogger(__name__)


def process_settings(data: bytes, minver: str) -> tuple[dict, list]:
    """Processes the contents of settings modules.

    Parameters
    ----------
    data
        The data to parse through.

    Returns
    -------
    dict
        The parsed settings.

    """
    settings = {}
    # First parse the settings right at the top of the data block.
    technique, params_dtypes = technique_params_dtypes[data[0x0000]]
    logger.debug("Found technique '%s'.", technique)
    settings["technique"] = technique
    for offset, (dtype, name) in settings_dtypes.items():
        settings[name] = dgutils.read_value(data, offset, dtype)
    # Then determine the technique parameters. The parameters' offset
    # changes depending on the technique present and apparently on some
    # other factor that is unclear to me.
    params_offset = None
    offsets = (
        0x0572,
        0x1845,
        0x1846,
        0x1847,
    )
    for offset in offsets:
        n_params = dgutils.read_value(data, offset + 0x0002, "<u2")
        logger.debug("Trying to find %d technique params at 0x%x.", n_params, offset)
        for dtype, versions in params_dtypes:
            logger.debug(f"{minver=} {versions=} {len(dtype)=} {n_params=}")
            if minver in versions and len(dtype) == n_params:
                params_dtype, params_offset = dtype, offset
                logger.debug("Determined %d parameters at 0x%x.", n_params, offset)
                break
        if params_offset is not None:
            break
    if params_offset is None:
        raise NotImplementedError("Unknown parameter offset or technique dtype.")
    logger.debug("Reading number of parameter sequences at 0x%x.", params_offset)
    ns = dgutils.read_value(data, params_offset, "<u2")
    logger.debug("Reading %d parameter sequences of %d parameters.", ns, n_params)
    rawparams = np.frombuffer(
        data,
        offset=params_offset + 0x0004,
        dtype=params_dtype,
        count=ns,
    )
    pardicts = [dict(zip(value.dtype.names, value.item())) for value in rawparams]
    params = []
    for pardict in pardicts:
        for k, v in pardict.items():
            # MPR quirk: I_range off by one
            if k == "I_range":
                v += 1
            pardict[k] = param_from_key(k, v, to_str=True)
            # Handle NaNs and +/-Inf in params here
            if np.isnan(v) or np.isinf(v):
                pardict[k] = str(v)
        params.append(pardict)
    return settings, params


def parse_columns(column_ids: list[int]) -> tuple[list, list, list, dict]:
    """Puts together column info from a list of data column IDs.

    Note
    ----
    The binary layout of the data in the `.mpr` file is described by a
    sequence of column IDs. Some column IDs relate to (flags) which are
    all packed into a single byte.

    Parameters
    ----------
    column_ids
        A list of column IDs.

    Returns
    -------
    tuple[list, list, list, dict]
        The column names, dtypes, units and a dictionary of flag names
        and bitmasks.

    """
    names = []
    dtypes = []
    units = []
    flags = {}
    for id in column_ids:
        if id in flag_columns:
            bitmask, name = flag_columns[id]
            flags[name] = bitmask
            # Flags column only needs to be added once.
            if "flags" not in names:
                names.append("flags")
                dtypes.append("|u1")
                units.append(None)
        elif id in data_columns:
            dtype, name, unit = data_columns[id]
            if name in names:
                logger.warning("Duplicate column '%s' with unit '%s'.", name, unit)
                name = f"duplicate {name}"
            names.append(name)
            dtypes.append(dtype)
            units.append(unit)
        else:
            name = f"unknown_{len(names)}"
            logger.warning("Unknown column ID %d was assigned into '%s'.", id, name)
            names.append(name)
            dtypes.append("<f4")
            units.append(None)
    return names, dtypes, units, flags


def process_data(
    data: bytes,
    version: int,
    Eranges: list[float],
    Iranges: list[float],
    controls: list[str],
):
    """Processes the contents of data modules.

    Parameters
    ----------
    data
        The data to parse through.

    version
        Module version from the data module header.

    Returns
    -------
    list[dict]
        Processed data ([{column -> value}, ..., {column -> value}]). If
        the column unit is set to None, the value is an int. Otherwise,
        the value is a dict with value ("n"), sigma ("s"), and unit
        ("u").

    """
    n_datapoints = dgutils.read_value(data, 0x0000, "<u4")
    n_columns = dgutils.read_value(data, 0x0004, "|u1")
    if version in {10, 11}:
        column_ids = np.frombuffer(data, offset=0x005, dtype=">u2", count=n_columns)
    elif version in {2, 3}:
        column_ids = np.frombuffer(data, offset=0x005, dtype="<u2", count=n_columns)
    logger.debug("Found %d columns with IDs: %s", n_columns, column_ids)
    # Length of each datapoint depends on number and IDs of columns.
    namelist, dtypelist, unitlist, flaglist = parse_columns(column_ids)
    units = {k: v for k, v in zip(namelist, unitlist) if v is not None}
    data_dtype = np.dtype(list(zip(namelist, dtypelist)))
    # Depending on module version, datapoints start at different offsets.
    if version in {10, 11}:
        offset = 0x3EF
    elif version == 2:
        offset = 0x195
    elif version == 3:
        offset = 0x196
    else:
        raise NotImplementedError(f"Unknown data module version: {version}")
    allvals = dict()
    allmeta = dict()
    values = np.frombuffer(data, offset=offset, dtype=data_dtype, count=n_datapoints)
    values = [dict(zip(value.dtype.names, value.item())) for value in values]
    warn_I_range = False
    warn_Ns = False
    for vi, vals in enumerate(values):
        # Lets split this into two loops: get the indices first, then the data
        for (name, value), unit in list(zip(vals.items(), unitlist)):
            if name.startswith("unknown_"):
                continue
            elif unit is None:
                intv = int(value)
                if name == "I Range":
                    vals[name] = param_from_key("I_range", intv)
                else:
                    vals[name] = intv
        if flaglist:
            flag_bits = vals.pop("flags")
            for name, bitmask in flaglist.items():
                # Two's complement hack to find the position of the
                # rightmost set bit.
                shift = (bitmask & -bitmask).bit_length() - 1
                # Rightshift flag by that amount.
                vals[name] = (flag_bits & bitmask) >> shift

        Ns = vals.get("Ns", 0)
        # Manually merged/appended mpr files have a mysteriously larger Ns
        if Ns >= len(Eranges):
            warn_Ns = True
            Ns = len(Eranges) - 1
        Erange = Eranges[Ns]
        Irstr = Iranges[Ns]
        if "I Range" in vals:
            Irstr = vals["I Range"]
        Irange = param_from_key("I_range", Irstr, to_str=False)

        # I Range can be None if it's set to "Auto", "PAC" or other such string.
        if Irange is None:
            warn_I_range = True
            Irange = 1.0

        if "control_V_I" in vals:
            icv = controls[Ns]
            name = "control_I" if icv in {"I", "C"} else "control_V"  # f"control_{icv}"
            vals[name] = vals.pop("control_V_I")
            units[name] = "mA" if icv in {"I", "C"} else "V"
        devs = get_devs(vals=vals, units=units, Erange=Erange, Irange=Irange)
        dgutils.append_dicts(vals, devs, allvals, allmeta, li=vi)
    if warn_I_range:
        logger.warning("I Range could not be understood, defaulting to 1 A.")
    if warn_Ns:
        logger.warning("Ns found in data exceeds Ns in header, using last defined Ns.")

    ds = dgutils.dicts_to_dataset(allvals, allmeta, units, fulldate=False)
    return ds


def process_log(data: bytes) -> dict:
    """Processes the contents of log modules.

    Parameters
    ----------
    data
        The data to parse through.

    Returns
    -------
    dict
        The parsed log.

    """
    log = {}
    for offset, (dtype, name) in log_dtypes.items():
        log[name] = dgutils.read_value(data, offset, dtype)
    return log


def process_loop(data: bytes) -> dict:
    """Processes the contents of loop modules.

    Parameters
    ----------
    data
        The data to parse through.

    Returns
    -------
    dict
        The parsed loops.

    """
    n_indexes = dgutils.read_value(data, 0x0000, "<u4")
    indexes = np.frombuffer(data, offset=0x0004, dtype="<u4", count=n_indexes)
    return {"n_indexes": n_indexes, "indexes": indexes}


def process_ext(data: bytes) -> dict:
    """Processes the contents of external device modules.

    Parameters
    ----------
    data
        The data to parse through.

    Returns
    -------
    dict
        The parsed log.

    """
    ext = {}
    for offset, (dtype, name) in extdev_dtypes.items():
        ext[name] = dgutils.read_value(data, offset, dtype)

    return ext


def process_modules(contents: bytes) -> tuple[dict, list, list, dict, dict]:
    """Handles the processing of all modules.

    Parameters
    ----------
    contents
        The contents of an .mpr file, minus the file magic.

    Returns
    -------
    tuple[dict, list, dict, dict]
        The processed settings, data, log, and loop modules. If they are
        not present in the provided modules, returns None instead.

    """
    modules = contents.split(b"MODULE")[1:]
    settings = log = loop = ext = None
    for module in modules:
        for mhd in module_header_dtypes:
            header = dgutils.read_value(module, 0x0000, mhd)
            if len(module) == mhd.itemsize + header["length"]:
                version = header.get("newver", 0) + header["oldver"]
                logger.debug(
                    "Parsed module header with length %d, version %s",
                    header["length"],
                    version,
                )
                break
        else:
            raise RuntimeError("Unknown module header.")
        name = header["short_name"].strip()
        # We need to determine file version from the header to be able to select correct
        # dtypes. Unfortunately, the header["oldver"] of the "VMP Set" module is always
        # set to 0. However, the newer versions of this module include the "max_length"
        # entry as well as an "newver" key set to 10.
        if version >= 10:
            minver = "11.50"
        # The oldest version we have in test files is 10.40.
        else:
            minver = "10.40"

        logger.debug("Read '%s' with version '%s' ('%s')", name, version, minver)
        module_data = module[mhd.itemsize :]
        if name == "VMP Set":
            settings, params = process_settings(module_data, minver)
            Eranges = []
            Iranges = []
            ctrls = []
            for el in params:
                E_range_max = el.get("E_range_max", float("inf"))
                E_range_min = el.get("E_range_min", float("-inf"))
                Eranges.append(E_range_max - E_range_min)
                Iranges.append(el.get("I_range", "Auto"))
                if "set_I/C" in el:
                    ctrls.append(el["set_I/C"])
                elif "apply_I/C" in el:
                    ctrls.append(el["apply_I/C"])
                else:
                    ctrls.append(None)
        elif name == "VMP data":
            ds = process_data(module_data, version, Eranges, Iranges, ctrls)
        elif name == "VMP LOG":
            log = process_log(module_data)
        elif name == "VMP loop":
            loop = process_loop(module_data)
        elif name == "VMP ExtDev":
            ext = process_ext(module_data)
        else:
            raise NotImplementedError(f"Unknown module: {name}.")
    if ext is not None:
        settings.update(ext)
    return settings, params, ds, log, loop


def extract(
    *,
    fn: str,
    timezone: str,
    **kwargs: dict,
) -> DataTree:
    file_magic = b"BIO-LOGIC MODULAR FILE\x1a                         \x00\x00\x00\x00"
    with open(fn, "rb") as mpr_file:
        assert mpr_file.read(len(file_magic)) == file_magic, "invalid file magic"
        mpr = mpr_file.read()
    settings, params, ds, log, loop = process_modules(mpr)
    assert settings is not None, "no settings module"
    assert ds is not None, "no data module"
    # Arrange all the data into the correct format.
    # TODO: Metadata could be handled in a nicer way.
    metadata = {"settings": settings, "params": params}
    if log is None:
        logger.warning("No 'log' module present in mpr file. Timestamps incomplete.")
        start_time = 0
        fulldate = False
    else:
        metadata["log"] = log
        start_time = dgutils.ole_to_uts(log["ole_timestamp"], timezone=timezone)
        fulldate = True
    if "time" in ds:
        ds["uts"] = ds["time"] + start_time
    else:
        ds["uts"] = [start_time]
    if fulldate:
        del ds.attrs["fulldate"]
    ds.attrs["original_metadata"] = metadata
    return DataTree(ds)
