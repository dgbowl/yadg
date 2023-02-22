import logging
import pandas as pd
from typing import Any
from zoneinfo import ZoneInfo
import numpy as np
from ...dgutils.dateutils import ole_to_uts
from ..eclabcommon.techniques import technique_params_dtypes, param_from_key, get_resolution

from .mpr_columns import (
    module_header_dtype,
    settings_dtypes,
    flag_columns,
    data_columns,
    log_dtypes,
    extdev_dtypes,
)

logger = logging.getLogger(__name__)


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


def process_settings(data: bytes) -> tuple[dict, list]:
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
    settings["technique"] = technique
    for offset, (dtype, name) in settings_dtypes.items():
        settings[name] = _read_value(data, offset, dtype)
    # Then determine the technique parameters. The parameters' offset
    # changes depending on the technique present and apparently on some
    # other factor that is unclear to me.
    params_offset = None
    for offset in (0x0572, 0x1845, 0x1846):
        logger.debug("Trying to find the technique parameters at 0x%x.", offset)
        n_params = _read_value(data, offset + 0x0002, "<u2")
        for dtype in params_dtypes:
            if len(dtype) == n_params:
                params_dtype, params_offset = dtype, offset
                logger.debug("Determined %d parameters at 0x%x.", n_params, offset)
                break
        if params_offset is not None:
            break
    if params_offset is None:
        raise NotImplementedError("Unknown parameter offset or technique dtype.")
    logger.debug("Reading number of parameter sequences at 0x%x.", params_offset)
    ns = _read_value(data, params_offset, "<u2")
    logger.debug("Reading %d parameter sequences of %d parameters.", ns, n_params)
    rawparams = _read_values(data, params_offset + 0x0004, params_dtype, ns)
    params = []
    for pardict in rawparams:
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
            names.append(name)
            dtypes.append(dtype)
            units.append(unit)
        else:
            name = f"unknown_{len(names)}"
            logger.warning("Unknown column ID '%d' was assigned into '%s'.", id, name)
            names.append(name)
            dtypes.append("<f4")
            units.append("")
    return names, dtypes, units, flags


def process_data(
    data: bytes, version: int, Eranges: list[float], Iranges: list[float]
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
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
    namelist, dtypelist, unitlist, flaglist = parse_columns(column_ids)
    units = {k: v for k, v in zip(namelist, unitlist) if v is not None}
    data_dtype = np.dtype(list(zip(namelist, dtypelist)))
    # Depending on module version, datapoints start at 0x0195 or 0x0196.
    if version == 2:
        offset = 0x0195
    elif version == 3:
        offset = 0x0196
    else:
        raise NotImplementedError(f"Unknown data module version: {version}")
    records = {}
    records["nominal"] = _read_values(data, offset, data_dtype, n_datapoints)
    records["sigma"] = []
    for datapoint in records["nominal"]:
        # Lets split this into two loops: get the indices first, then the data
        for (name, value), unit in list(zip(datapoint.items(), unitlist)):
            if unit is None:
                intv = int(value)
                if name == "I Range":
                    datapoint[name] = param_from_key("I_range", intv)
                else:
                    datapoint[name] = intv
        if flaglist:
            # logger.debug("Extracting flag values.")
            flag_bits = datapoint.pop("flags")
            for name, bitmask in flaglist.items():
                # Two's complement hack to find the position of the
                # rightmost set bit.
                shift = (bitmask & -bitmask).bit_length() - 1
                # Rightshift flag by that amount.
                datapoint[name] = (flag_bits & bitmask) >> shift

        if "Ns" in datapoint:
            Erange = Eranges[datapoint["Ns"]]
            Irstr = Iranges[datapoint["Ns"]]
        else:
            Erange = Eranges[0]
            Irstr = Iranges[0]
        if "I Range" in datapoint:
            Irstr = datapoint["I Range"]
        Irange = param_from_key("I_range", Irstr, to_str=False)
        sigmas = {}
        for name, value in datapoint.items():
            unit = units.get(name)
            if unit is None:
                continue
            sigmas[name] = get_resolution(name, value, unit, Erange, Irange)
        records["sigma"].append(sigmas)
    
    nominal = pd.DataFrame.from_records(records["nominal"])
    sigma = pd.DataFrame.from_records(records["sigma"])
    
    return nominal, sigma, units


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
        log[name] = _read_value(data, offset, dtype)
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
    n_indexes = _read_value(data, 0x0000, "<u4")
    indexes = _read_values(data, 0x0004, "<u4", n_indexes)
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
        ext[name] = _read_value(data, offset, dtype)

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
    settings = data = log = loop = ext = None
    for module in modules:
        header = _read_value(module, 0x0000, module_header_dtype)
        name = header["short_name"].strip()
        logger.debug("Read '%s' module.", name)
        module_data = module[module_header_dtype.itemsize :]
        if name == "VMP Set":
            settings, params = process_settings(module_data)
            Eranges = []
            Iranges = []
            for el in params:
                E_range_max = el.get("E_range_max", float("inf"))
                E_range_min = el.get("E_range_min", float("-inf"))
                Eranges.append(E_range_max - E_range_min)
                Iranges.append(el.get("I_range", "Auto"))
        elif name == "VMP data":
            data = process_data(module_data, header["version"], Eranges, Iranges)
        elif name == "VMP LOG":
            log = process_log(module_data)
        elif name == "VMP loop":
            loop = process_loop(module_data)
        elif name == "VMP ExtDev":
            ext = process_ext(module_data)
        else:
            raise NotImplementedError(f"Unknown module: {name}.")
    if ext is not None:
        # replace names, units, and correct sigmas in data with headers present in ext
        for k in {"Analog IN 1", "Analog IN 2"}:
            parts = ext[k].split("/")
            if len(parts) == 1:
                n = parts[0]
                u = " "
            else:
                n, u = parts
            for i in range(len(data)):
                if k in data[i]:
                    data[i][n] = data[i].pop(k)
                    data[i][n]["u"] = u
                    ds = ext[k + " max x"] - ext[k + " min x"]
                    ds = ds / (ext[k + " max V"] - ext[k + " min V"])
                    data[i][n]["s"] = data[i][n]["s"] * ds
        # shove the whole ext into settings
        settings.update(ext)
    return settings, params, data, log, loop


def process(
    fn: str,
    timezone: ZoneInfo,
) -> tuple[list, dict, bool]:
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
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and the full date tag. For mpr files,
        the full date is specified if the "LOG" module is present.

    """
    file_magic = b"BIO-LOGIC MODULAR FILE\x1a                         \x00\x00\x00\x00"
    with open(fn, "rb") as mpr_file:
        assert mpr_file.read(len(file_magic)) == file_magic, "invalid file magic"
        mpr = mpr_file.read()
    settings, params, data, log, loop = process_modules(mpr)
    nominal, sigma, units = data
    assert settings is not None, "no settings module"
    assert data is not None, "no data module"
    # Arrange all the data into the correct format.
    # TODO: Metadata could be handled in a nicer way.
    metadata = {"settings": settings, "params": params}
    if log is None:
        logger.warning("No 'log' module present in mpr file. Timestamps incomplete.")
        start_time = 0
        fulldate = False
    else:
        metadata["log"] = log
        start_time = ole_to_uts(log["ole_timestamp"], timezone=timezone)
        fulldate = True
    metadata["fulldate"] = fulldate
    if fulldate:
        nominal["uts"] = nominal["time"] + start_time
        sigma["uts"] = nominal["uts"]
        nominal.set_index("uts", inplace=True)
        sigma.set_index("uts", inplace=True)
    return metadata, nominal, sigma, units
