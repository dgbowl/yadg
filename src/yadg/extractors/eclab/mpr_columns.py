import numpy as np

# Module header starting after each MODULE keyword.
module_header_dtypes = (
    np.dtype(
        [
            ("short_name", "|S10"),
            ("long_name", "|S25"),
            ("max_length", "<u4"),
            ("length", "<u4"),
            ("oldver", "<u4"),
            ("newver", "<u4"),
            ("date", "|S8"),
        ]
    ),
    np.dtype(
        [
            ("short_name", "|S10"),
            ("long_name", "|S25"),
            ("length", "<u4"),
            ("oldver", "<u4"),
            ("date", "|S8"),
        ]
    ),
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
    1: (0b00000011, "mode"),
    2: (0b00000100, "ox or red"),
    3: (0b00001000, "error"),
    21: (0b00010000, "control changes"),
    31: (0b00100000, "Ns changes"),
    # NOTE: I think the missing bitmask (0b01000000) is a stop bit. It
    # sometimes appears in the flag byte of the very last data point.
    65: (0b10000000, "counter inc."),
}


# Maps the data column ID bytes to the corresponding dtype, name and
# unit.
data_columns = {
    4: ("<f8", "time", "s"),
    5: ("<f4", "control", "V/mA"),
    6: ("<f4", "Ewe", "V"),
    7: ("<f8", "dq", "mA·h"),
    8: ("<f4", "I", "mA"),
    9: ("<f4", "Ece", "V"),
    11: ("<f8", "<I>", "mA"),
    13: ("<f8", "(Q-Qo)", "mA·h"),
    15: ("<f4", "Phase(Z1)", "deg"),
    16: ("<f4", "Analog IN 1", "V"),
    17: ("<f4", "Analog IN 2", "V"),
    19: ("<f4", "control_V", "V"),
    20: ("<f4", "control_I", "mA"),
    23: ("<f8", "dQ", "mA·h"),
    24: ("<f8", "cycle number", None),
    32: ("<f4", "freq", "Hz"),
    33: ("<f4", "|Ewe|", "V"),
    34: ("<f4", "|I|", "A"),
    35: ("<f4", "Phase(Z)", "deg"),
    36: ("<f4", "|Z|", "Ω"),
    37: ("<f4", "Re(Z)", "Ω"),
    38: ("<f4", "-Im(Z)", "Ω"),
    39: ("<u2", "I Range", None),
    45: ("<f4", "|Z1|", "Ω"),
    46: ("<f4", "|Z2|", "Ω"),
    69: ("<f4", "Rwe", "Ω"),
    70: ("<f4", "Pwe", "W"),
    74: ("<f8", "|Energy|", "W·h"),
    75: ("<f4", "Analog OUT", "V"),
    76: ("<f4", "<I>", "mA"),
    77: ("<f4", "<Ewe>", "V"),
    78: ("<f4", "Cs⁻²", "µF⁻²"),
    96: ("<f4", "|Ece|", "V"),
    98: ("<f4", "Phase(Zce)", "deg"),
    99: ("<f4", "|Zce|", "Ω"),
    100: ("<f4", "Re(Zce)", "Ω"),
    101: ("<f4", "-Im(Zce)", "Ω"),
    105: ("<f4", "-Im(Z1)", "Ω"),
    106: ("<f4", "-Im(Z2)", "Ω"),
    110: ("<f8", "Energy ce", "W·h"),
    112: ("<f8", "Energy we", "W·h"),
    115: ("<f8", "Energy ce charge", "W·h"),
    116: ("<f8", "Energy ce discharge", "W·h"),
    123: ("<f8", "Energy we charge", "W·h"),
    124: ("<f8", "Energy we discharge", "W·h"),
    125: ("<f8", "Capacitance charge", "µF"),
    126: ("<f8", "Capacitance discharge", "µF"),
    131: ("<u2", "Ns", None),
    135: ("<f4", "<E1>", "V"),
    136: ("<f4", "<E2>", "V"),
    163: ("<f4", "|Estack|", "V"),
    166: ("<f4", "Phase(Zstack)", "deg"),
    167: ("<f4", "|Zstack|", "Ω"),
    168: ("<f4", "Rcmp", "Ω"),
    169: ("<f4", "Cs", "µF"),
    172: ("<f4", "Cp", "µF"),
    173: ("<f4", "Cp⁻²", "µF⁻²"),
    174: ("<f4", "<Ewe>", "V"),  # This column may conflict with ID 77 and 6.
    175: ("<f4", "|Zwe-ce|", "Ω"),
    176: ("<f4", "Re(Zwe-ce)", "Ω"),
    177: ("<f4", "-Im(Zwe-ce)", "Ω"),
    178: ("<f4", "(Q-Qo)", "C"),
    179: ("<f4", "dQ", "C"),
    182: ("<f8", "step time", "s"),
    185: ("<f4", "<Ece>", "V"),
    206: ("<f4", "Temperature", "°C"),
    211: ("<f8", "Q charge or discharge", "C"),
    212: ("<u4", "half cycle", None),
    213: ("<u4", "z cycle", None),
    215: ("<f4", "<Ece>", "V"),
    217: ("<f4", "THD Ewe", "%"),
    218: ("<f4", "THD I", "%"),
    219: ("<f4", "THD Ece", "%"),
    220: ("<f4", "NSD Ewe", "%"),
    221: ("<f4", "NSD I", "%"),
    222: ("<f4", "NSD Ece", "%"),
    223: ("<f4", "NSR Ewe", "%"),
    224: ("<f4", "NSR I", "%"),
    225: ("<f4", "NSR Ece", "%"),
    230: ("<f4", "|Ewe h2|", "V"),
    231: ("<f4", "|Ewe h3|", "V"),
    232: ("<f4", "|Ewe h4|", "V"),
    233: ("<f4", "|Ewe h5|", "V"),
    234: ("<f4", "|Ewe h6|", "V"),
    235: ("<f4", "|Ewe h7|", "V"),
    236: ("<f4", "|I h2|", "A"),
    237: ("<f4", "|I h3|", "A"),
    238: ("<f4", "|I h4|", "A"),
    239: ("<f4", "|I h5|", "A"),
    240: ("<f4", "|I h6|", "A"),
    241: ("<f4", "|I h7|", "A"),
    242: ("<f4", "|Ece h2|", "V"),
    243: ("<f4", "|Ece h3|", "V"),
    244: ("<f4", "|Ece h4|", "V"),
    245: ("<f4", "|Ece h5|", "V"),
    246: ("<f4", "|Ece h6|", "V"),
    247: ("<f4", "|Ece h7|", "V"),
}

# Conflict resolution map. If both the outer and inner column ID are present,
# the meaning of the outer column ID is set to the entry below.
conflict_columns = {
    174: {
        6: ("<f4", "Phase(Zwe-ce)", "deg"),
        77: ("<f4", "Phase(Zwe-ce)", "deg"),
    },
}

technique_dependent_ids = {
    6: {
        "BCD": "Ecell",
    }
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
