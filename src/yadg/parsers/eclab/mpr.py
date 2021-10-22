#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read BioLogic's EC-Lab binary modular files into dicts.

This code is an adaptation of the `galvani` module by Chris Kerr
(https://github.com/echemdata/galvani) and builds on the work done by
the previous civilian service member working on the project, Jonas
Krieger.

While there where mostly only `modules` and the `module header` before,
now pretty much the entire file structure is there for a few relevant
techniques.

Author:         Nicolas Vetsch (veni@empa.ch / nicolas.vetsch@gmx.ch)
Organisation:   EMPA Dübendorf, Materials for Energy Conversion (501)
Date:           2021-09-29

"""
import logging
from io import TextIOWrapper
from typing import Any

import numpy as np
import pandas as pd
from numpy.lib import recfunctions as rfn

from .techniques import technique_params_dtypes

# Module header at the top of every MODULE block.
module_header_dtype = np.dtype([
    ('short_name', '|S10'),
    ('long_name', '|S25'),
    ('length', '<u4'),
    ('version', '<u4'),
    ('date', '|S8'),
])

# Relates the offset in the settings DATA to the corresponding dtype.
settings_dtypes = {
    0x0007: ('comments', 'pascal'),
    0x0107: ('active_material_mass', '<f4'),
    0x010b: ('at_x', '<f4'),
    0x010f: ('molecular_weight', '<f4'),
    0x0113: ('atomic_weight', '<f4'),
    0x0117: ('acquisition_start', '<f4'),
    0x011b: ('e_transferred', '<u2'),
    0x011e: ('electrode_material', 'pascal'),
    0x01c0: ('electrolyte', 'pascal'),
    0x0211: ('electrode_area', '<f4'),
    0x0215: ('reference_electrode', 'pascal'),
    0x024c: ('characteristic_mass', '<f4'),
    0x025c: ('battery_capacity', '<f4'),
    0x0260: ('battery_capacity_unit', '|u1'),
    # The compliance limits are not always at this offset.
    # 0x19d2: ('compliance_min', '<f4'),1
    # 0x19d6: ('compliance_max', '<f4'),
}

# Maps the flag column ID bytes to the corresponding dtype and bitmask.
flag_column_dtypes = {
    0x0001: ('mode', '|u1', 0x03),
    0x0002: ('ox/red', '|b1', 0x04),
    0x0003: ('error', '|b1', 0x08),
    0x0015: ('control changes', '|b1', 0x10),
    0x001F: ('Ns changes', '|b1', 0x20),
    # NOTE: I think the missing bitmask (0x40) is a stop bit. It
    # appears in the flag bytes of the very last data point.
    0x0041: ('counter inc.', '|b1', 0x80),
}

# Maps the data column ID bytes to the corresponding dtype and bitmask.
data_column_dtypes = {
    0x0004: ('time/s', '<f8'),
    0x0005: ('control/V/mA', '<f4'),
    0x0006: ('Ewe/V', '<f4'),
    0x0007: ('dq/mA.h', '<f8'),
    0x0008: ('I/mA', '<f4'),
    0x0009: ('Ece/V', '<f4'),
    0x000b: ('<I>/mA', '<f8'),
    0x000d: ('(Q-Qo)/mA.h', '<f8'),
    0x0010: ('Analog IN 1/V', '<f4'),
    0x0013: ('control/V', '<f4'),
    0x0014: ('control/mA', '<f4'),
    0x0017: ('dQ/mA.h', '<f8'),
    0x0018: ('cycle number', '<f8'),
    0x0020: ('freq/Hz', '<f4'),
    0x0021: ('|Ewe|/V', '<f4'),
    0x0022: ('|I|/A', '<f4'),
    0x0023: ('Phase(Z)/deg', '<f4'),
    0x0024: ('|Z|/Ohm', '<f4'),
    0x0025: ('Re(Z)/Ohm', '<f4'),
    0x0026: ('-Im(Z)/Ohm', '<f4'),
    0x0027: ('I Range', '<u2'),
    0x0046: ('P/W', '<f4'),
    0x004a: ('Energy/W.h', '<f8'),
    0x004b: ('Analog OUT/V', '<f4'),
    0x004c: ('<I>/mA', '<f4'),
    0x004d: ('<Ewe>/V', '<f4'),
    0x004e: ('Cs-2/µF-2', '<f4'),
    0x0060: ('|Ece|/V', '<f4'),
    0x0062: ('Phase(Zce)/deg', '<f4'),
    0x0063: ('|Zce|/Ohm', '<f4'),
    0x0064: ('Re(Zce)/Ohm', '<f4'),
    0x0065: ('-Im(Zce)/Ohm', '<f4'),
    0x007b: ('Energy charge/W.h', '<f8'),
    0x007c: ('Energy discharge/W.h', '<f8'),
    0x007d: ('Capacitance charge/µF', '<f8'),
    0x007e: ('Capacitance discharge/µF', '<f8'),
    0x0083: ('Ns', '<u2'),
    0x00a3: ('|Estack|/V', '<f4'),
    0x00a8: ('Rcmp/Ohm', '<f4'),
    0x00a9: ('Cs/µF', '<f4'),
    0x00ac: ('Cp/µF', '<f4'),
    0x00ad: ('Cp-2/µF-2', '<f4'),
    0x00ae: ('<Ewe>/V', '<f4'),
    0x00f1: ('|E1|/V', '<f4'),
    0x00f2: ('|E2|/V', '<f4'),
    0x010f: ('Phase(Z1) / deg', '<f4'),
    0x0110: ('Phase(Z2) / deg', '<f4'),
    0x012d: ('|Z1|/Ohm', '<f4'),
    0x012e: ('|Z2|/Ohm', '<f4'),
    0x014b: ('Re(Z1)/Ohm', '<f4'),
    0x014c: ('Re(Z2)/Ohm', '<f4'),
    0x0169: ('-Im(Z1)/Ohm', '<f4'),
    0x016a: ('-Im(Z2)/Ohm', '<f4'),
    0x0187: ('<E1>/V', '<f4'),
    0x0188: ('<E2>/V', '<f4'),
    0x01a6: ('Phase(Zstack)/deg', '<f4'),
    0x01a7: ('|Zstack|/Ohm', '<f4'),
    0x01a8: ('Re(Zstack)/Ohm', '<f4'),
    0x01a9: ('-Im(Zstack)/Ohm', '<f4'),
    0x01aa: ('<Estack>/V', '<f4'),
    0x01ae: ('Phase(Zwe-ce)/deg', '<f4'),
    0x01af: ('|Zwe-ce|/Ohm', '<f4'),
    0x01b0: ('Re(Zwe-ce)/Ohm', '<f4'),
    0x01b1: ('-Im(Zwe-ce)/Ohm', '<f4'),
    0x01b2: ('(Q-Qo)/C', '<f4'),
    0x01b3: ('dQ/C', '<f4'),
    0x01b9: ('<Ece>/V', '<f4'),
    0x01ce: ('Temperature/°C', '<f4'),
    0x01d3: ('Q charge/discharge/mA.h', '<f8'),
    0x01d4: ('half cycle', '<u4'),
    0x01d5: ('z cycle', '<u4'),
    0x01d7: ('<Ece>/V', '<f4'),
    0x01d9: ('THD Ewe/%', '<f4'),
    0x01da: ('THD I/%', '<f4'),
    0x01dc: ('NSD Ewe/%', '<f4'),
    0x01dd: ('NSD I/%', '<f4'),
    0x01df: ('NSR Ewe/%', '<f4'),
    0x01e0: ('NSR I/%', '<f4'),
    0x01e6: ('|Ewe h2|/V', '<f4'),
    0x01e7: ('|Ewe h3|/V', '<f4'),
    0x01e8: ('|Ewe h4|/V', '<f4'),
    0x01e9: ('|Ewe h5|/V', '<f4'),
    0x01ea: ('|Ewe h6|/V', '<f4'),
    0x01eb: ('|Ewe h7|/V', '<f4'),
    0x01ec: ('|I h2|/A', '<f4'),
    0x01ed: ('|I h3|/A', '<f4'),
    0x01ee: ('|I h4|/A', '<f4'),
    0x01ef: ('|I h5|/A', '<f4'),
    0x01f0: ('|I h6|/A', '<f4'),
    0x01f1: ('|I h7|/A', '<f4'),
}

# Relates the offset in the log DATA to the corresponding dtype.
log_dtypes = {
    # TODO: Sort this out.
    # 0x01d7: ('safety_limits_t', '<f4'),
    # 0x01??: ('safety_limits_ewe_max', '<f4'),
    # 0x01??: ('safety_limits_ewe_min', '<f4'),
    # 0x01??: ('safety_limits_i', '<f4'),
    # 0x01??: ('safety_limits_q', '<f4'),
    # 0x01??: ('safety_limits_an_in1', '<f4'),
    # 0x01??: ('safety_limits_an_in2', '<f4'),
    # 0x01??: ('safety_limits_e_stack_max', '<f4'),
    # 0x01??: ('safety_limits_e_stack_min', '<f4'),
    # 0x01??: ('safety_limits_flags', '|u1'),
    0x01f8: ('ewe_ctrl_min', '<f4'),
    0x01fc: ('ewe_ctrl_max', '<f4'),
    # 0x0200: ('safety_limits', '') # TODO The safety limits are in here maybe?
    0x0249: ('ole_timestamp', '<f8'),
    0x0251: ('filename', 'pascal'),
    0x0351: ('host', 'pascal'),
    0x0384: ('address', 'pascal'),
    0x03b7: ('ec_lab_version', 'pascal'),
    0x03be: ('server_version', 'pascal'),
    0x03c5: ('interpreter_version', 'pascal'),
    0x03cf: ('device_sn', 'pascal'),
    # The log also seems to contain the settings again. These are left
    # away for now.
    # TODO: Parse the settings again here.
    # NOTE: Looking at the .mpl files, the log module appears to consist of
    # multiple 'modify on' sections that start with an OLE timestamp.
    0x0922: ('averaging_points', '|u1'),
}


def _read_pascal_string(bytes: bytes) -> bytes:
    """Parses a variable-length length-prefixed string.

    Parameters
    ----------
    bytes
        The bytes of the string starting at the length-prefix byte.

    Returns
    -------
    bytes
        The bytes that contain the string.

    """
    if len(bytes) < bytes[0] + 1:
        raise ValueError("Insufficient number of bytes.")
    return bytes[1:bytes[0]+1]


def _read_value(data: bytes, offset: int, dtype) -> Any:
    """Reads a single value from a buffer at a certain offset.

    Just a handy wrapper for np.frombuffer().

    Parameters
    ----------
    data
        An object that exposes the buffer interface. Here always bytes.
    offset
        Start reading the buffer from this offset (in bytes).
    dtype
        Data-type to read in.

    Returns
    -------
    Any
        The unpacked value from the buffer.

    """
    if dtype == 'pascal':
        # This allows the use of 'pascal' in all of the dtype maps.
        return _read_pascal_string(data[offset:])
    return np.frombuffer(data, offset=offset, dtype=dtype, count=1)[0]


def _read_values(data: bytes, offset: int, dtype, count) -> Any:
    """Reads in multiple values from a buffer starting at offset.

    Just a handy wrapper for np.frombuffer() with count >= 1.

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
    return np.frombuffer(data, offset=offset, dtype=dtype, count=count)


def _parse_settings(data: bytes) -> dict:
    """Parses through the contents of settings modules.

    Unfortunately this data contains a few pascal strings and some 0x00
    padding, which seems to be incompatible with simply specifying a
    struct in np.dtype and using np.frombuffer() to read the whole thing
    in.

    The offsets from the start of the data part are hardcoded in as they
    do not seem to change. (Maybe watch out for very long comments that
    span over the entire padding.)

    Parameters
    ----------
    data
        The module data to parse through.

    Returns
    -------
    dict
        A dict with the contents parsed and structured.

    """
    logging.debug("Parsing `.mpr` settings module...")
    settings = {}
    # First parse the settings right at the top of the data block.
    technique, params_dtype = technique_params_dtypes[data[0x0000]]
    settings['technique'] = technique
    for item in settings_dtypes.items():
        offset, (name, dtype) = item
        settings[name] = _read_value(data, offset, dtype)
    # Then determine the technique parameters. The parameters' offset
    # changes depending on the technique present.
    params_offset = None
    for offset in {0x0572, 0x1846, 0x1845}:
        n_params = _read_value(data, offset+0x0002, '<u2')
        if isinstance(params_dtype, dict):
            for dtype in params_dtype.values():
                if len(dtype) == n_params:
                    params_dtype = dtype
                    params_offset = offset
        elif len(params_dtype) == n_params:
            params_offset = offset
    if params_offset is None:
        raise NotImplementedError(
            "Unknown parameter offset or unrecognized technique dtype.")
    ns = _read_value(data, params_offset, '<u2')
    logging.debug(
        f"Reading {ns} parameter sequences starting at an offset of "
        f"{params_offset} bytes from settings data block...")
    params_array = _read_values(data, params_offset+0x0004, params_dtype, ns)
    params = []
    for n in range(ns):
        params_n = {key: params_array[n][key] for key in params_dtype.names}
        params.append(params_n)
    settings['params'] = params
    return settings


def _construct_data_dtype(column_ids: list[int]) -> tuple[np.dtype, dict]:
    """Puts together a dtype from a list of data column IDs.

    Note
    ----
    The binary layout of the data in the MPR file is described by the
    sequence of column ID numbers in the file header. This function
    converts that sequence into a numpy dtype which can then be used to
    load data from the file with np.frombuffer().

    Some column IDs refer to small values (flags) which are packed into
    a single byte. The second return value is a dict describing the bit
    masks with which to extract these columns from the flags byte.

    Parameters
    ----------
    column_ids
        A list of column IDs.

    Returns
    -------
    tuple[nd.dtype, dict]
        A numpy dtype for the given columns, a dict of flags.

    """
    column_dtypes = []
    flags = {}
    for id in column_ids:
        if id in flag_column_dtypes:
            name, dtype, bitmask = flag_column_dtypes[id]
            flags[name] = (bitmask, dtype)
            if ('flags', '|u1') in column_dtypes:
                continue
            column_dtypes.append(('flags', '|u1'))
        elif id in data_column_dtypes:
            column_dtypes.append(data_column_dtypes[id])
        else:
            raise NotImplementedError(
                f"Column ID {id} after column {column_dtypes[-1][0]} "
                f"is unknown.")
    return np.dtype(column_dtypes), flags


def _parse_data(data: bytes, version: int) -> dict:
    """Parses through the contents of data modules.

    Parameters
    ----------
    data
        The module data to parse through.

    Returns
    -------
    dict
        A modified dict with the parsed contents.

    """
    logging.debug("Parsing `.mpr` data module...")
    n_data_points = _read_value(data, 0x0000, '<u4')
    n_columns = _read_value(data, 0x0004, '|u1')
    column_ids = _read_values(data, 0x0005, '<u2', n_columns)
    logging.debug("Constructing column dtype from column IDs...")
    data_dtype, flags = _construct_data_dtype(column_ids)
    # Depending on the version in the header, the data points start at a
    # different point in the data part.
    logging.debug(f"Reading {n_data_points} data points...")
    if version == 2:
        data_points = _read_values(data, 0x0195, data_dtype, n_data_points)
    elif version == 3:
        data_points = _read_values(data, 0x0196, data_dtype, n_data_points)
    else:
        data_points = _read_values(data, 0x0196, data_dtype, n_data_points)
    if flags:
        # Extract flag values via bitmask (if flags are present).
        flag_values = np.array(
            data_points['flags'],
            dtype=[('flags', '|u1')])
        for item in flags.items():
            name, (bitmask, flag_dtype) = item
            values = np.array(
                data_points['flags'] & bitmask,
                dtype=[(name, flag_dtype)])
            flag_values = rfn.merge_arrays(
                seqarrays=[flag_values, values],
                flatten=True)
        # The flags column has to be removed from the original record to
        # get everything in the order I prefer (if flags column exists).
        data_points = rfn.rec_drop_fields(data_points, 'flags')
        data_points = rfn.merge_arrays(
            [flag_values, data_points],
            flatten=True)
    data_points = pd.DataFrame.from_records(data_points)
    data_points = data_points.to_dict(orient='records')
    data = {
        'n_data_points': n_data_points,
        'n_columns': n_columns,
        'data_points': data_points,
    }
    return data


def _parse_log(data: bytes) -> dict:
    """Parses through the contents of log modules.

    Parameters
    ----------
    data
        The module data to parse through.

    Returns
    -------
    dict
        A modified dict with the parsed contents.

    """
    logging.debug("Parsing `.mpr` log module...")
    log = {}
    for item in log_dtypes.items():
        offset, (name, dtype) = item
        log[name] = _read_value(data, offset, dtype)
    return log


def _parse_loop(data: bytes) -> dict:
    """Parses through the contents of loop modules.

    Parameters
    ----------
    data
        The module data to parse through.

    Returns
    -------
    dict
        A modified dict with the parsed contents.

    """
    logging.debug("Parsing `.mpr` loop module...")
    n_indexes = _read_value(data, 0x0000, '<u4')
    indexes = list(_read_values(data, 0x0004, '<u4', n_indexes))
    loop = {
        'n_indexes': n_indexes,
        'indexes': indexes,
    }
    return loop


def _read_modules(file: TextIOWrapper) -> list:
    """Reads in modules from the given file object.

    Parameters
    ----------
    file
        The open file object to read.

    Returns
    -------
    list
        Returns a list of modules with corresponding header and data.

    """
    modules = []
    while file.read(len(b'MODULE')) == b'MODULE':
        header_bytes = file.read(module_header_dtype.itemsize)
        header_array = np.frombuffer(
            header_bytes, module_header_dtype, count=1)
        header = {key: header_array[key][0]
                  for key in module_header_dtype.names}
        bytes = file.read(header['length'])
        modules.append({'header': header, 'data': bytes})
    return modules


def parse_mpr(path: str) -> list[dict]:
    """Parses an EC-Lab MPR file.

    Parameters
    ----------
    path
        Filepath of the EC-Lab MPR file to read in.

    Returns
    -------
    list[dict]
        A list of modules containing parsed module data.

    """
    file_magic = (b'BIO-LOGIC MODULAR FILE\x1a                         '
                  b'\x00\x00\x00\x00')
    with open(path, 'rb') as mpr:
        if mpr.read(len(file_magic)) != file_magic:
            raise ValueError("Invalid file magic for given `.mpr` file.")
        logging.info("Reading `.mpr` modules...")
        modules = _read_modules(mpr)
        logging.info("Parsing `.mpr` module data...")
        for module in modules:
            name = module['header']['short_name']
            if name == b'VMP Set   ':
                module['data'] = _parse_settings(module['data'])
            elif name == b'VMP data  ':
                # The data points' offset depends on the module version.
                version = module['header']['version']
                module['data'] = _parse_data(module['data'], version)
            elif name == b'VMP LOG   ':
                module['data'] = _parse_log(module['data'])
            elif name == b'VMP loop  ':
                module['data'] = _parse_loop(module['data'])
        return modules
