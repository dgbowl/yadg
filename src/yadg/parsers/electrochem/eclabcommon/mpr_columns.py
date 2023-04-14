import numpy as np

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
    0x0002: (0b00000100, "ox or red"),
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
    0x0005: ("<f4", "control_V_I", "V/mA"),
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
    0x0024: ("<f4", "|Z|", "Ω"),
    0x0025: ("<f4", "Re(Z)", "Ω"),
    0x0026: ("<f4", "-Im(Z)", "Ω"),
    0x0027: ("<u2", "I Range", None),
    0x0046: ("<f4", "P", "W"),
    0x004A: ("<f8", "Energy", "W·h"),
    0x004B: ("<f4", "Analog OUT", "V"),
    0x004C: ("<f4", "<I>", "mA"),
    0x004D: ("<f4", "<Ewe>", "V"),
    0x004E: ("<f4", "Cs⁻²", "µF⁻²"),
    0x0060: ("<f4", "|Ece|", "V"),
    0x0062: ("<f4", "Phase(Zce)", "deg"),
    0x0063: ("<f4", "|Zce|", "Ω"),
    0x0064: ("<f4", "Re(Zce)", "Ω"),
    0x0065: ("<f4", "-Im(Zce)", "Ω"),
    0x007B: ("<f8", "Energy charge", "W·h"),
    0x007C: ("<f8", "Energy discharge", "W·h"),
    0x007D: ("<f8", "Capacitance charge", "µF"),
    0x007E: ("<f8", "Capacitance discharge", "µF"),
    0x0083: ("<u2", "Ns", None),
    0x00A3: ("<f4", "|Estack|", "V"),
    0x00A8: ("<f4", "Rcmp", "Ω"),
    0x00A9: ("<f4", "Cs", "µF"),
    0x00AC: ("<f4", "Cp", "µF"),
    0x00AD: ("<f4", "Cp⁻²", "µF⁻²"),
    0x00AE: ("<f4", "<Ewe>", "V"),
    0x00F1: ("<f4", "|E1|", "V"),
    0x00F2: ("<f4", "|E2|", "V"),
    0x010F: ("<f4", "Phase(Z1)", "deg"),
    0x0110: ("<f4", "Phase(Z2)", "deg"),
    0x012D: ("<f4", "|Z1|", "Ω"),
    0x012E: ("<f4", "|Z2|", "Ω"),
    0x014B: ("<f4", "Re(Z1)", "Ω"),
    0x014C: ("<f4", "Re(Z2)", "Ω"),
    0x0169: ("<f4", "-Im(Z1)", "Ω"),
    0x016A: ("<f4", "-Im(Z2)", "Ω"),
    0x0187: ("<f4", "<E1>", "V"),
    0x0188: ("<f4", "<E2>", "V"),
    0x01A6: ("<f4", "Phase(Zstack)", "deg"),
    0x01A7: ("<f4", "|Zstack|", "Ω"),
    0x01A8: ("<f4", "Re(Zstack)", "Ω"),
    0x01A9: ("<f4", "-Im(Zstack)", "Ω"),
    0x01AA: ("<f4", "<Estack>", "V"),
    0x01AE: ("<f4", "Phase(Zwe-ce)", "deg"),
    0x01AF: ("<f4", "|Zwe-ce|", "Ω"),
    0x01B0: ("<f4", "Re(Zwe-ce)", "Ω"),
    0x01B1: ("<f4", "-Im(Zwe-ce)", "Ω"),
    0x01B2: ("<f4", "(Q-Qo)", "C"),
    0x01B3: ("<f4", "dQ", "C"),
    0x01B9: ("<f4", "<Ece>", "V"),
    0x01CE: ("<f4", "Temperature", "°C"),
    0x01D3: ("<f8", "Q charge or discharge", "mA·h"),
    0x01D4: ("<u4", "half cycle", None),
    0x01D5: ("<u4", "z cycle", None),
    0x01D7: ("<f4", "<Ece>", "V"),
    0x01D9: ("<f4", "THD Ewe", "%"),
    0x01DA: ("<f4", "THD I", "%"),
    0x01DB: ("<f4", "THD Ece", "%"),
    0x01DC: ("<f4", "NSD Ewe", "%"),
    0x01DD: ("<f4", "NSD I", "%"),
    0x01DE: ("<f4", "NSD Ece", "%"),
    0x01DF: ("<f4", "NSR Ewe", "%"),
    0x01E0: ("<f4", "NSR I", "%"),
    0x01E1: ("<f4", "NSR Ece", "%"),
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
    0x01F2: ("<f4", "|Ece h2|", "V"),
    0x01F3: ("<f4", "|Ece h3|", "V"),
    0x01F4: ("<f4", "|Ece h4|", "V"),
    0x01F5: ("<f4", "|Ece h5|", "V"),
    0x01F6: ("<f4", "|Ece h6|", "V"),
    0x01F7: ("<f4", "|Ece h7|", "V"),
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


extdev_dtypes = {
    0x0036: ("pascal", "Analog IN 1"),
    0x0052: ("<f4", "Analog IN 1 max V"),
    0x0056: ("<f4", "Analog IN 1 min V"),
    0x005A: ("<f4", "Analog IN 1 max x"),
    0x005E: ("<f4", "Analog IN 1 min x"),
    0x0063: ("pascal", "Analog IN 2"),
    0x007F: ("<f4", "Analog IN 2 max V"),
    0x0083: ("<f4", "Analog IN 2 min V"),
    0x0087: ("<f4", "Analog IN 2 max x"),
    0x008B: ("<f4", "Analog IN 2 min x"),
}
