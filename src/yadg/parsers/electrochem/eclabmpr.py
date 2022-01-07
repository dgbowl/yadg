"""Processing of BioLogic's EC-Lab binary modular files.

This code is partly an adaptation of the [`galvani` module by Chris
Kerr](https://github.com/echemdata/galvani) and builds on the work done
by the previous civilian service member working on the project, Jonas
Krieger.

File Structure of `.mpr` Files
``````````````````````````````

At a top level, `.mpr` files are made up of a number of modules,
separated by the `MODULE` keyword. In all the files I have seen, the
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

After splitting the entire file on `MODULE`, each module starts with a
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


Structure of Parsed Data
````````````````````````

*EIS Techniques (PEIS/GEIS)*

.. code-block:: yaml

    - fn   !!str
    - uts  !!float
    - raw:
        traces:
          "{{ trace_number }}":
            "{{ col1 }}":
              [!!int, ...]
            "{{ col2 }}":
              {n: [!!float, ...], s: [!!float, ...], u: !!str}

*All Other Techniques*

.. code-block:: yaml

    - fn   !!str
    - uts  !!float
    - raw:
        "{{ col1 }}":  !!int
        "{{ col2 }}":
          {n: !!float, s: !!float, u: !!str}

.. codeauthor:: Nicolas Vetsch <vetschnicolas@gmail.com>
"""
import logging
import math
from collections import defaultdict
from typing import Any

import numpy as np
from yadg.dgutils.dateutils import ole_to_uts
from yadg.parsers.electrochem.eclabtechniques import technique_params_dtypes

# Module header starting after each MODULE keyword.
module_header_dtype = np.dtype(
    [
        ("short_name", "|S10"),
        ("long_name", "|S25"),
        ("length", "<u4"),
        ("version", "<u4"),
        ("date", "|S8"),
    ]
)


# Relates the offset in the settings data to the corresponding dtype and
# name. Maybe watch out for very long pascal strings as they may span
# over the entire zero padding and shift the offsets.
settings_dtypes = {
    0x0007: ("pascal", "comments"),
    0x0107: ("<f4", "active_material_mass"),
    0x010B: ("<f4", "at_x"),
    0x010F: ("<f4", "molecular_weight"),
    0x0113: ("<f4", "atomic_weight"),
    0x0117: ("<f4", "acquisition_start"),
    0x011B: ("<u2", "e_transferred"),
    0x011E: ("pascal", "electrode_material"),
    0x01C0: ("pascal", "electrolyte"),
    0x0211: ("<f4", "electrode_area"),
    0x0215: ("pascal", "reference_electrode"),
    0x024C: ("<f4", "characteristic_mass"),
    0x025C: ("<f4", "battery_capacity"),
    0x0260: ("|u1", "battery_capacity_unit"),
    # NOTE: The compliance limits are apparently not always at this
    # offset, hence commented out...
    # 0x19d2: ("<f4", "compliance_min"),
    # 0x19d6: ("<f4", "compliance_max"),
}


# Maps the flag column ID bytes to the corresponding bitmask and name.
flag_columns = {
    0x0001: (0b00000011, "mode"),
    0x0002: (0b00000100, "ox/red"),
    0x0003: (0b00001000, "error"),
    0x0015: (0b00010000, "control changes"),
    0x001F: (0b00100000, "Ns changes"),
    # NOTE: I think the missing bitmask (0b01000000) is a stop bit. It
    # sometimes appears in the flag byte of the very last data point.
    0x0041: (0b10000000, "counter inc."),
}


# Maps the data column ID bytes to the corresponding dtype, name and
# unit.
data_columns = {
    0x0004: ("<f8", "time", "s"),
    0x0005: ("<f4", "control_V/I", "V/mA"),
    0x0006: ("<f4", "Ewe", "V"),
    0x0007: ("<f8", "dq", "mA·h"),
    0x0008: ("<f4", "I", "mA"),
    0x0009: ("<f4", "Ece", "V"),
    0x000B: ("<f8", "<I>", "mA"),
    0x000D: ("<f8", "(Q-Qo)", "mA·h"),
    0x0010: ("<f4", "Analog IN 1", "V"),
    0x0011: ("<f4", "Analog IN 2", "V"),
    0x0013: ("<f4", "control_V", "V"),
    0x0014: ("<f4", "control_I", "mA"),
    0x0017: ("<f8", "dQ", "mA·h"),
    0x0018: ("<f8", "cycle number", None),
    0x0020: ("<f4", "freq", "Hz"),
    0x0021: ("<f4", "|Ewe|", "V"),
    0x0022: ("<f4", "|I|", "A"),
    0x0023: ("<f4", "Phase(Z)", "deg"),
    0x0024: ("<f4", "|Z|", "Ohm"),
    0x0025: ("<f4", "Re(Z)", "Ohm"),
    0x0026: ("<f4", "-Im(Z)", "Ohm"),
    0x0027: ("<u2", "I Range", None),
    0x0046: ("<f4", "P", "W"),
    0x004A: ("<f8", "Energy", "W·h"),
    0x004B: ("<f4", "Analog OUT", "V"),
    0x004C: ("<f4", "<I>", "mA"),
    0x004D: ("<f4", "<Ewe>", "V"),
    0x004E: ("<f4", "Cs⁻²", "µF⁻²"),
    0x0060: ("<f4", "|Ece|", "V"),
    0x0062: ("<f4", "Phase(Zce)", "deg"),
    0x0063: ("<f4", "|Zce|", "Ohm"),
    0x0064: ("<f4", "Re(Zce)", "Ohm"),
    0x0065: ("<f4", "-Im(Zce)", "Ohm"),
    0x007B: ("<f8", "Energy charge", "W·h"),
    0x007C: ("<f8", "Energy discharge", "W·h"),
    0x007D: ("<f8", "Capacitance charge", "µF"),
    0x007E: ("<f8", "Capacitance discharge", "µF"),
    0x0083: ("<u2", "Ns", None),
    0x00A3: ("<f4", "|Estack|", "V"),
    0x00A8: ("<f4", "Rcmp", "Ohm"),
    0x00A9: ("<f4", "Cs", "µF"),
    0x00AC: ("<f4", "Cp", "µF"),
    0x00AD: ("<f4", "Cp⁻²", "µF⁻²"),
    0x00AE: ("<f4", "<Ewe>", "V"),
    0x00F1: ("<f4", "|E1|", "V"),
    0x00F2: ("<f4", "|E2|", "V"),
    0x010F: ("<f4", "Phase(Z1)", "deg"),
    0x0110: ("<f4", "Phase(Z2)", "deg"),
    0x012D: ("<f4", "|Z1|", "Ohm"),
    0x012E: ("<f4", "|Z2|", "Ohm"),
    0x014B: ("<f4", "Re(Z1)", "Ohm"),
    0x014C: ("<f4", "Re(Z2)", "Ohm"),
    0x0169: ("<f4", "-Im(Z1)", "Ohm"),
    0x016A: ("<f4", "-Im(Z2)", "Ohm"),
    0x0187: ("<f4", "<E1>", "V"),
    0x0188: ("<f4", "<E2>", "V"),
    0x01A6: ("<f4", "Phase(Zstack)", "deg"),
    0x01A7: ("<f4", "|Zstack|", "Ohm"),
    0x01A8: ("<f4", "Re(Zstack)", "Ohm"),
    0x01A9: ("<f4", "-Im(Zstack)", "Ohm"),
    0x01AA: ("<f4", "<Estack>", "V"),
    0x01AE: ("<f4", "Phase(Zwe-ce)", "deg"),
    0x01AF: ("<f4", "|Zwe-ce|", "Ohm"),
    0x01B0: ("<f4", "Re(Zwe-ce)", "Ohm"),
    0x01B1: ("<f4", "-Im(Zwe-ce)", "Ohm"),
    0x01B2: ("<f4", "(Q-Qo)", "C"),
    0x01B3: ("<f4", "dQ", "C"),
    0x01B9: ("<f4", "<Ece>", "V"),
    0x01CE: ("<f4", "Temperature", "°C"),
    0x01D3: ("<f8", "Q charge/discharge", "mA·h"),
    0x01D4: ("<u4", "half cycle", None),
    0x01D5: ("<u4", "z cycle", None),
    0x01D7: ("<f4", "<Ece>", "V"),
    0x01D9: ("<f4", "THD Ewe", "%"),
    0x01DA: ("<f4", "THD I", "%"),
    0x01DC: ("<f4", "NSD Ewe", "%"),
    0x01DD: ("<f4", "NSD I", "%"),
    0x01DF: ("<f4", "NSR Ewe", "%"),
    0x01E0: ("<f4", "NSR I", "%"),
    0x01E6: ("<f4", "|Ewe h2|", "V"),
    0x01E7: ("<f4", "|Ewe h3|", "V"),
    0x01E8: ("<f4", "|Ewe h4|", "V"),
    0x01E9: ("<f4", "|Ewe h5|", "V"),
    0x01EA: ("<f4", "|Ewe h6|", "V"),
    0x01EB: ("<f4", "|Ewe h7|", "V"),
    0x01EC: ("<f4", "|I h2|", "A"),
    0x01ED: ("<f4", "|I h3|", "A"),
    0x01EE: ("<f4", "|I h4|", "A"),
    0x01EF: ("<f4", "|I h5|", "A"),
    0x01F0: ("<f4", "|I h6|", "A"),
    0x01F1: ("<f4", "|I h7|", "A"),
}


# Relates the offset in log data to the corresponding dtype and name.
# NOTE: The safety limits are maybe at 0x200?
# NOTE: The log also seems to contain the settings again. These are left
# away for now.
# NOTE: Looking at .mpl files, the log module appears to consist of
# multiple 'modify on' sections, each starting with an OLE timestamp.
log_dtypes = {
    0x0009: ("|u1", "channel_number"),
    0x00AB: ("<u2", "channel_sn"),
    0x01F8: ("<f4", "Ewe_ctrl_min"),
    0x01FC: ("<f4", "Ewe_ctrl_max"),
    0x0249: ("<f8", "ole_timestamp"),
    0x0251: ("pascal", "filename"),
    0x0351: ("pascal", "host"),
    0x0384: ("pascal", "address"),
    0x03B7: ("pascal", "ec_lab_version"),
    0x03BE: ("pascal", "server_version"),
    0x03C5: ("pascal", "interpreter_version"),
    0x03CF: ("pascal", "device_sn"),
    0x0922: ("|u1", "averaging_points"),
}


def _read_pascal_string(pascal_bytes: bytes, encoding: str = "windows-1252") -> str:
    """Parses a length-prefixed string given some encoding.

    Parameters
    ----------
    bytes
        The bytes of the string starting at the length-prefix byte.

    encoding
        The encoding of the string to be converted.

    Returns
    -------
    str
        The string decoded from the input bytes.

    """
    if len(pascal_bytes) < pascal_bytes[0] + 1:
        raise ValueError("Insufficient number of bytes.")
    string_bytes = pascal_bytes[1 : pascal_bytes[0] + 1]
    return string_bytes.decode(encoding)


def _read_value(
    data: bytes, offset: int, dtype: np.dtype, encoding: str = "windows-1252"
) -> Any:
    """Reads a single value from a buffer at a certain offset.

    Just a handy wrapper for np.frombuffer() With the added benefit of
    allowing the 'pascal' keyword as an indicator for a length-prefixed
    string.

    The read value is converted to a built-in datatype using
    np.dtype.item().

    Parameters
    ----------
    data
        An object that exposes the buffer interface. Here always bytes.

    offset
        Start reading the buffer from this offset (in bytes).

    dtype
        Data-type to read in.

    encoding
        The encoding of the bytes to be converted.

    Returns
    -------
    Any
        The unpacked and converted value from the buffer.

    """
    if dtype == "pascal":
        # Allow the use of 'pascal' in all of the dtype maps.
        return _read_pascal_string(data[offset:])
    value = np.frombuffer(data, offset=offset, dtype=dtype, count=1)
    item = value.item()
    if value.dtype.names:
        item = [i.decode(encoding) if isinstance(i, bytes) else i for i in item]
        return dict(zip(value.dtype.names, item))
    return item.decode(encoding) if isinstance(item, bytes) else item


def _read_values(data: bytes, offset: int, dtype, count) -> list:
    """Reads in multiple values from a buffer starting at offset.

    Just a handy wrapper for np.frombuffer() with count >= 1.

    The read values are converted to a list of built-in datatypes using
    np.ndarray.tolist().

    Parameters
    ----------
    data
        An object that exposes the buffer interface. Here always bytes.

    offset
        Start reading the buffer from this offset (in bytes).

    dtype
        Data-type to read in.

    count
        Number of items to read. -1 means all data in the buffer.

    Returns
    -------
    Any
        The values read from the buffer as specified by the arguments.

    """
    values = np.frombuffer(data, offset=offset, dtype=dtype, count=count)
    if values.dtype.names:
        return [dict(zip(value.dtype.names, value.item())) for value in values]
    # The ndarray.tolist() method converts numpy scalars to built-in
    # scalars, hence not just list(values).
    return values.tolist()


def _process_settings(data: bytes) -> tuple[dict, list]:
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
    technique, params_dtype = technique_params_dtypes[data[0x0000]]
    settings["technique"] = technique
    for offset, (dtype, name) in settings_dtypes.items():
        settings[name] = _read_value(data, offset, dtype)
    # Then determine the technique parameters. The parameters' offset
    # changes depending on the technique present and apparently on some
    # other factor that is unclear to me.
    params_offset = None
    for offset in (0x0572, 0x1845, 0x1846):
        logging.debug(f"Trying to find the technique parameters at {offset:x}.")
        n_params = _read_value(data, offset + 0x0002, "<u2")
        if isinstance(params_dtype, list):
            # The params_dtype has multiple possible lengths if a list.
            for dtype in params_dtype:
                if len(dtype) == n_params:
                    params_dtype, params_offset = dtype, offset
        elif len(params_dtype) == n_params:
            params_offset = offset
            logging.debug(f"Determined {n_params} parameters at 0x{offset:x}.")
            break
    if params_offset is None:
        raise NotImplementedError("Unknown parameter offset or technique dtype.")
    logging.debug(f"Reading number of parameter sequences at 0x{params_offset:x}.")
    ns = _read_value(data, params_offset, "<u2")
    logging.debug(f"Reading {ns} parameter sequences of {n_params} parameters.")
    params = _read_values(data, params_offset + 0x0004, params_dtype, ns)
    return settings, params


def _parse_columns(column_ids: list[int]) -> tuple[list, list, list, dict]:
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
            names.append(name)
            dtypes.append(dtype)
            units.append(unit)
        else:
            raise NotImplementedError(f"Unknown column ID: {id}")
    return names, dtypes, units, flags


def _process_data(data: bytes, version: int) -> list[dict]:
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
    n_datapoints = _read_value(data, 0x0000, "<u4")
    n_columns = _read_value(data, 0x0004, "|u1")
    column_ids = _read_values(data, 0x0005, "<u2", n_columns)
    # Length of each datapoint depends on number and IDs of columns.
    names, dtypes, units, flags = _parse_columns(column_ids)
    data_dtype = np.dtype(list(zip(names, dtypes)))
    # Depending on module version, datapoints start at 0x0195 or 0x0196.
    if version == 2:
        offset = 0x0195
    elif version == 3:
        offset = 0x0196
    else:
        raise NotImplementedError(f"Unknown data module version: {version}")
    datapoints = _read_values(data, offset, data_dtype, n_datapoints)
    for datapoint in datapoints:
        for (name, value), unit in list(zip(datapoint.items(), units)):
            # TODO: Using the unit of least precision (spacing between
            # two floats) as a measure of uncertainty for now.
            if unit is None:
                datapoint[name] = int(value)
                continue
            datapoint[name] = {"n": value, "s": math.ulp(value), "u": unit}
        if flags:
            logging.debug("Extracting flag values.")
            flag_bits = datapoint.pop("flags")
            for name, bitmask in flags.items():
                # Two's complement hack to find the position of the
                # rightmost set bit.
                shift = (bitmask & -bitmask).bit_length() - 1
                # Rightshift flag by that amount.
                datapoint[name] = (flag_bits & bitmask) >> shift
    return datapoints


def _process_log(data: bytes) -> dict:
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
        log[name] = _read_value(data, offset, dtype)
    return log


def _process_loop(data: bytes) -> dict:
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
    n_indexes = _read_value(data, 0x0000, "<u4")
    indexes = _read_values(data, 0x0004, "<u4", n_indexes)
    return {"n_indexes": n_indexes, "indexes": indexes}


def _process_modules(contents: bytes) -> tuple[dict, list, list, dict, dict]:
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
    settings = data = log = loop = None
    for module in modules:
        header = _read_value(module, 0x0000, module_header_dtype)
        name = header["short_name"].strip()
        logging.debug(f"Read '{name}' module.")
        module_data = module[module_header_dtype.itemsize :]
        if name == "VMP Set":
            settings, params = _process_settings(module_data)
        elif name == "VMP data":
            data = _process_data(module_data, header["version"])
        elif name == "VMP LOG":
            log = _process_log(module_data)
        elif name == "VMP loop":
            loop = _process_loop(module_data)
        else:
            raise NotImplementedError(f"Unknown module: {name}.")
    return settings, params, data, log, loop


def process(
    fn: str, encoding: str = "windows-1252", timezone: str = "localtime"
) -> tuple[list, dict]:
    """Processes EC-Lab raw data binary files.

    Parameters
    ----------
    fn
        The file containing the data to parse.

    encoding
        Encoding of ``fn``, by default "windows-1252".

    timezone
        A string description of the timezone. Default is "localtime".

    Returns
    -------
    (data, metadata) : tuple[list, dict]
        Tuple containing the timesteps and metadata.

    """
    file_magic = b"BIO-LOGIC MODULAR FILE\x1a                         \x00\x00\x00\x00"
    with open(fn, "rb") as mpr_file:
        assert mpr_file.read(len(file_magic)) == file_magic, "invalid file magic"
        mpr = mpr_file.read()
    settings, params, data, log, loop = _process_modules(mpr)
    assert settings is not None, "no settings module"
    assert data is not None, "no data module"
    assert log is not None, "no log module"
    # Arrange all the data into the correct format.
    # TODO: Metadata could be handled in a nicer way.
    metadata = {"settings": settings, "params": params, "log": log}
    start_time = ole_to_uts(log["ole_timestamp"])
    timesteps = []
    # If the technique is an impedance spectroscopy, split it into
    # traces at different cycle numbers and put everything into a single
    # timestep.
    if settings["technique"] in {"PEIS", "GEIS"}:
        # Grouping by cycle.
        cycles = defaultdict(list)
        for d in data:
            cycles[d["cycle number"]].append(d)
        # Casting cycles into traces.
        cols = data[0].keys()
        traces = {}
        for num, cycle in cycles.items():
            traces[str(num)] = {col: [d[col] for d in cycle] for col in cols}
        # Casting nominal values and sigmas into lists.
        for num, trace in traces.items():
            for key, val in trace.items():
                if not isinstance(val[0], dict):
                    continue
                trace[key] = {k: [i[k] for i in val] for k in val[0]}
                # Reducing unit list to just a string.
                trace[key]["u"] = set(trace[key]["u"]).pop()
        uts = start_time + data[0]["time"]["n"]
        timesteps = [{"uts": uts, "fn": fn, "raw": {"traces": traces}}]
        return timesteps, metadata
    # All other techniques have multiple timesteps.
    for d in data:
        uts = start_time + d["time"]["n"]
        timesteps.append({"fn": fn, "uts": uts, "raw": d})
    return timesteps, metadata
