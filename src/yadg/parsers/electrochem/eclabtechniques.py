"""Implemented technique parameters.

Implemented techniques:
    CA - Chronoamperometry / Chronocoulometry
    CP - Chronopotentiometry
    CV - Cyclic Voltammetry
    GCPL - Galvanostatic Cycling with Potential Limitation
    GEIS - Galvano Electrochemical Impedance Spectroscopy
    LOOP - Loop
    LSV - Linear Sweep Voltammetry
    MB - Modulo Bat
    OCV - Open Circuit Voltage
    PEIS - Potentio Electrochemical Impedance Spectroscopy
    WAIT - Wait
    ZIR - IR compensation (PEIS)

"""
import re

import numpy as np


# Short helper function for constructing params.
def _prepend_ns(settings: list[str], params: list) -> list[str]:
    """Prepends the 'Ns' parameter to the parameters if present.

    Parameters
    ----------
    settings
        The list of settings from the start of an .mpt or .mps file.
    params
        A list containing the first part of the technique parameter
        names. The Ns is prepended to this if present in the settings.

    Returns
    -------
    list[str]
        The 'Ns'-prepended parameters or the unchanged parameters.

    """
    ns_match = re.search(r"^Ns.+", "\n".join(settings))
    if ns_match:
        return ["Ns"] + params
    return params


################# Chronoamperometry / Chronocoulometry #################
def _ca_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the CA technique."""
    params = [
        "Ei",
        "Ei_vs",
        "ti",
        "Imax",
        "Imax_unit",
        "Imin",
        "Imin_unit",
        "dQM",
        "dQM_unit",
        "record",
        "dI",
        "dI_unit",
        "dQ",
        "dQ_unit",
        "dt",
        "dta",
        "E_range_min",
        "E_range_max",
        "I_range",
        "I_range_min",
        "I_range_max",
        "I_range_init",
        "bandwidth",
        "goto_Ns",
        "nc_cycles",
    ]
    return _prepend_ns(settings, params)


_ca_params_dtype = np.dtype(
    [
        ("Ei", "<f4"),
        ("Ei_vs", "|u1"),
        ("ti", "<f4"),
        ("Imax", "<f4"),
        ("Imax_unit", "|u1"),
        ("Imin", "<f4"),
        ("Imin_unit", "|u1"),
        ("dQM", "<f4"),
        ("dQM_unit", "|u1"),
        ("record", "|u1"),
        ("dI", "<f4"),
        ("dI_unit", "|u1"),
        ("dQ", "<f4"),
        ("dQ_unit", "|u1"),
        ("dt", "<f4"),
        ("dta", "<f4"),
        ("E_range_min", "<f4"),
        ("E_range_max", "<f4"),
        ("I_range", "|u1"),
        ("I_range_min", "|u1"),
        ("I_range_max", "|u1"),
        ("I_range_init", "|u1"),
        ("bandwidth", "u1"),
        ("goto_Ns", "<u4"),
        ("nc_cycles", "<u4"),
    ]
)


########################## Chronopotentiometry #########################
def _cp_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the CP technique."""
    params = [
        "Is",
        "Is_unit",
        "Is_vs",
        "ts",
        "EM",
        "dQM",
        "dQM_unit",
        "record",
        "dEs",
        "dts",
        "E_range_min",
        "E_range_max",
        "I_range",
        "bandwidth",
        "goto_Ns",
        "nc_cycles",
    ]
    return _prepend_ns(settings, params)


_cp_params_dtype = np.dtype(
    [
        ("Is", "<f4"),
        ("Is_unit", "|u1"),
        ("Is_vs", "|u1"),
        ("ts", "<f4"),
        ("EM", "<f4"),
        ("dQM", "<f4"),
        ("dQM_unit", "|u1"),
        ("record", "|u1"),
        ("dEs", "<f4"),
        ("dts", "<f4"),
        ("E_range_min", "<f4"),
        ("E_range_max", "<f4"),
        ("I_range", "|u1"),
        ("bandwidth", "|u1"),
        ("goto_Ns", "<u4"),
        ("nc_cycles", "<u4"),
    ]
)

########################## Cyclic Voltammetry ##########################
def _cv_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the CV technique."""
    params = [
        "Ei",
        "Ei_vs",
        "dE/dt",
        "dE/dt_unit",
        "E1",
        "E1_vs",
        "step_percent",
        "N",
        "E_range_min",
        "E_range_max",
        "I_range",
        "I_range_min",
        "I_range_max",
        "I_range_init",
        "bandwidth",
        "E2",
        "E2_vs",
        "nc_cycles",
        "reverse_scan",
        "Ef",
        "Ef_vs",
    ]
    return params


_cv_params_dtype = np.dtype(
    [
        ("Ei", "<f4"),
        ("Ei_vs", "|u1"),
        ("dE/dt", "<f4"),
        ("dE/dt_unit", "|u1"),
        ("E1", "<f4"),
        ("E1_vs", "|u1"),
        ("step_percent", "|u1"),
        ("N", "<u4"),
        ("E_range_min", "<f4"),
        ("E_range_max", "<f4"),
        ("I_range", "|u1"),
        ("I_range_min", "|u1"),
        ("I_range_max", "|u1"),
        ("I_range_init", "|u1"),
        ("bandwidth", "u1"),
        ("E2", "<f4"),
        ("E2_vs", "|u1"),
        ("nc_cycles", "<u4"),
        ("reverse_scan", "|u1"),
        ("Ef", "<f4"),
        ("Ef_vs", "|u1"),
    ]
)

############ Galvanostatic Cycling with Potential Limitation ###########
def _gcpl_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the GCPL technique."""
    params = [
        "set_I/C",
        "Is",
        "Is_unit",
        "Is_vs",
        "N",
        "I_sign",
        "t1",
        "I_range",
        "bandwidth",
        "dE1",
        "dt1",
        "EM",
        "tM",
        "Im",
        "Im_unit",
        "dI/dt",
        "dI/dt_unit",
        "E_range_min",
        "E_range_max",
        "dq",
        "dq_unit",
        "dtq",
        "dQM",
        "dQM_unit",
        "dxM",
        "tR",
        "dER/dt",
        "dER",
        "dtR",
        "EL",
        "goto_Ns",
        "nc_cycles",
    ]
    return _prepend_ns(settings, params)


_gcpl_params_dtype = np.dtype(
    [
        ("set_I/C", "|u1"),
        ("Is", "<f4"),
        ("Is_unit", "|u1"),
        ("Is_vs", "|u1"),
        ("N", "f4"),
        ("I_sign", "|u1"),
        ("t1", "<f4"),
        ("I_range", "|u1"),
        ("bandwidth", "|u1"),
        ("dE1", "<f4"),
        ("dt1", "<f4"),
        ("EM", "<f4"),
        ("tM", "<f4"),
        ("Im", "<f4"),
        ("Im_unit", "|u1"),
        ("dI/dt", "<f4"),
        ("dI/dt_unit", "|u1"),
        ("E_range_min", "<f4"),
        ("E_range_max", "<f4"),
        ("dq", "<f4"),
        ("dq_unit", "|u1"),
        ("dtq", "<f4"),
        ("dQM", "<f4"),
        ("dQM_unit", "|u1"),
        ("dxM", "<f4"),
        ("tR", "<f4"),
        ("dER/dt", "<f4"),
        ("dER", "<f4"),
        ("dtR", "<f4"),
        ("EL", "<f4"),
        ("goto_Ns", "<u4"),
        ("nc_cycles", "<u4"),
    ]
)

############ Galvano Electrochemical Impedance Spectroscopy ############
def _geis_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the GEIS technique."""
    params = [
        "sine_mode",
        "Is",
        "Is_unit",
        "Is_vs",
        "tIs",
        "record",
        "dE",
        "dt",
        "fi",
        "fi_unit",
        "ff",
        "ff_unit",
        "Nd",
        "points",
        "spacing",
        "Ia/Va",
        "Ia",
        "Ia_unit",
        "va_pourcent",  # Random French parameter name?
        "pw",
        "Na",
        "corr",
    ]
    params = _prepend_ns(settings, params)
    lim_nb_match = re.search(r"^lim_nb\s+(?P<val>.+)", "\n".join(settings))
    if lim_nb_match:
        lim_nb = int(max(lim_nb_match["val"].split()))
        params.append("lim_nb")
        for i, __ in enumerate(range(lim_nb), 1):
            limit = [
                f"limit_type{i}",
                f"limit_comp{i}",
                f"limit_value{i}",
                f"limit_unit{i}",
            ]
            params += limit
    params += [
        "E_range_min",
        "E_range_max",
        "I_range",
        "bandwidth",
        "nc_cycles",
        "goto_Ns",
        "nr_cycles",
        "inc_cycle",
    ]
    return params


_geis_params_dtype = np.dtype(
    [
        ("sine_mode", "|u1"),
        ("Is", "<f4"),
        ("Is_unit", "|u1"),
        ("Is_vs", "|u1"),
        ("tIs", "<f4"),
        ("record", "|u1"),
        ("dE", "<f4"),
        ("dt", "<f4"),
        ("fi", "<f4"),
        ("fi_unit", "|u1"),
        ("ff", "<f4"),
        ("ff_unit", "|u1"),
        ("Nd", "<u4"),
        ("points", "|u1"),
        ("spacing", "|u1"),
        ("Ia/Va", "|u1"),
        ("Ia", "<f4"),
        ("Ia_unit", "|u1"),
        ("va_pourcent", "<f4"),
        ("pw", "<f4"),
        ("Na", "<u4"),
        ("corr", "|u1"),
        ("lim_nb", "|u1"),
        ("limit_type1", "|u1"),
        ("limit_comp1", "|u1"),
        ("limit_value1", "<f4"),
        ("limit_unit1", "|u1"),
        ("limit_type2", "|u1"),
        ("limit_comp2", "|u1"),
        ("limit_value2", "<f4"),
        ("limit_unit2", "|u1"),
        ("limit_type3", "|u1"),
        ("limit_comp3", "|u1"),
        ("limit_value3", "<f4"),
        ("limit_unit3", "|u1"),
        ("limit_type4", "|u1"),
        ("limit_comp4", "|u1"),
        ("limit_value4", "<f4"),
        ("limit_unit4", "|u1"),
        ("limit_type5", "|u1"),
        ("limit_comp5", "|u1"),
        ("limit_value5", "<f4"),
        ("limit_unit5", "|u1"),
        ("limit_type6", "|u1"),
        ("limit_comp6", "|u1"),
        ("limit_value6", "<f4"),
        ("limit_unit6", "|u1"),
        ("E_range_min", "<f4"),
        ("E_range_max", "<f4"),
        ("I_range", "|u1"),
        ("bandwidth", "|u1"),
        ("nc_cycles", "<u4"),
        ("goto_Ns", "<u4"),
        ("nr_cycles", "<u4"),
        ("inc_cycle", "<u4"),
    ]
)

################################# Loop #################################
def _loop_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the LOOP technique."""
    params = ["goto_Ne", "nt_times"]
    return params


####################### Linear Sweep Voltammetry #######################
def _lsv_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the LSV technique."""
    params = [
        "tR",
        "dER/dt",
        "dER",
        "dtR",
        "dE/dt",
        "dE/dt_unit",
        "Ei",
        "Ei_vs",
        "EL",
        "EL_vs",
        "record",
        "dI",
        "dI_unit",
        "tI",
        "step_percent",
        "N",
        "E_range_min",
        "E_range_max",
        "I_range",
        "I_range_min",
        "I_range_max",
        "I_range_init",
        "bandwidth",
    ]
    return params


####################### Linear Sweep Voltammetry #######################
_lsv_params_dtype = np.dtype(
    [
        ("tR", "<f4"),
        ("dER/dt", "<f4"),
        ("dER", "<f4"),
        ("dtR", "<f4"),
        ("dE/dt", "<f4"),
        ("dE/dt_unit", "|u1"),
        ("Ei", "<f4"),
        ("Ei_vs", "|u1"),
        ("EL", "<f4"),
        ("EL_vs", "|u1"),
        ("record", "|u1"),
        ("dI", "<f4"),
        ("dI_unit", "|u1"),
        ("tI", "<f4"),
        ("step_percent", "|u1"),
        ("N", "<u4"),
        ("E_range_min", "<f4"),
        ("E_range_max", "<f4"),
        ("I_range", "|u1"),
        ("I_range_min", "|u1"),
        ("I_range_max", "|u1"),
        ("I_range_init", "|u1"),
        ("bandwidth", "|u1"),
    ]
)


############################## Modulo Bat ##############################
def _mb_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the MB technique."""
    params = [
        "ctrl_type",
        "apply_I/C",
        "ctrl1_val",
        "ctrl1_val_unit",
        "ctrl1_val_vs",
        "ctrl2_val",
        "ctrl2_val_unit",
        "ctrl2_val_vs",
        "ctrl3_val",
        "ctrl3_val_unit",
        "ctrl3_val_vs",
        "N",
        "charge/discharge",
    ]
    params = _prepend_ns(settings, params)
    n1_match = re.search(r"^N1\s+", "\n".join(settings))
    if n1_match:
        n1 = [
            "charge/discharge_1",
            "apply_I/C_1",
            "N1",
            "ctrl4_val_unit",
            "ctrl4_val_vs",
        ]
        params += n1
    params += [
        "ctrl_seq",
        "ctrl_repeat",
        "ctrl_trigger",
        "ctrl_TO_t",
        "ctrl_TO_t_unit",
        "ctrl_Nd",
        "ctrl_Na",
        "ctrl_corr",
    ]
    lim_nb_match = re.search(r"^lim_nb\s+(?P<val>.+)", "\n".join(settings))
    if lim_nb_match:
        lim_nb = int(max(lim_nb_match["val"].split()))
        params.append("lim_nb")
        for i, __ in enumerate(range(lim_nb), 1):
            lim = [
                f"lim{i}_type",
                f"lim{i}_comp",
                f"lim{i}_Q",
                f"lim{i}_value",
                f"lim{i}_value_unit",
                f"lim{i}_action",
                f"lim{i}_seq",
            ]
            params += lim
    rec_nb_match = re.search(r"^rec_nb\s+(?P<val>.+)", "\n".join(settings))
    if rec_nb_match:
        rec_nb = int(max(rec_nb_match["val"].split()))
        params.append("rec_nb")
        for i, __ in enumerate(range(rec_nb), 1):
            rec = [f"rec{i}_type", f"rec{i}_value", f"rec{i}_value_unit"]
            params += rec
    params += [
        "E_range_min",
        "E_range_max",
        "I_range",
        "I_range_min",
        "I_range_max",
        "I_range_init",
        "auto_rest",
        "bandwidth",
    ]
    return params


_mb_params_dtypes = [
    np.dtype(
        [
            ("ctrl_type", "|u1"),
            ("apply_I/C", "|u1"),
            ("ctrl1_val", "<f4"),
            ("ctrl1_val_unit", "|u1"),
            ("ctrl1_val_vs", "|u1"),
            ("ctrl2_val", "<f4"),
            ("ctrl2_val_unit", "|u1"),
            ("ctrl2_val_vs", "|u1"),
            ("ctrl3_val", "<f4"),
            ("ctrl3_val_unit", "|u1"),
            ("ctrl3_val_vs", "|u1"),
            ("N", "<f4"),
            ("charge/discharge", "|u1"),
            ("charge/discharge_1", "|u1"),
            ("apply_I/C_1", "|u1"),
            ("N1", "<f4"),
            ("ctrl4_val", "<f4"),
            ("ctrl4_val_unit", "|u1"),
            ("ctrl_seq", "<u4"),
            ("ctrl_repeat", "<u4"),
            ("ctrl_trigger", "|u1"),
            ("ctrl_TO_t", "<f4"),
            ("ctrl_TO_t_unit", "|u1"),
            ("ctrl_Nd", "<u4"),
            ("ctrl_Na", "<u4"),
            ("ctrl_corr", "|u1"),
            ("lim_nb", "|u1"),
            ("lim1_type", "|u1"),
            ("lim1_comp", "|u1"),
            ("lim1_Q", "|u1"),
            ("lim1_value", "<f4"),
            ("lim1_value_unit", "|u1"),
            ("lim1_action", "|u1"),
            ("lim1_seq", "<u4"),
            ("lim2_type", "|u1"),
            ("lim2_comp", "|u1"),
            ("lim2_Q", "|u1"),
            ("lim2_value", "<f4"),
            ("lim2_value_unit", "|u1"),
            ("lim2_action", "|u1"),
            ("lim2_seq", "<u4"),
            ("lim3_type", "|u1"),
            ("lim3_comp", "|u1"),
            ("lim3_Q", "|u1"),
            ("lim3_value", "<f4"),
            ("lim3_value_unit", "|u1"),
            ("lim3_action", "|u1"),
            ("lim3_seq", "<u4"),
            ("rec_nb", "|u1"),
            ("rec1_type", "|u1"),
            ("rec1_value", "<f4"),
            ("rec1_value_unit", "|u1"),
            ("rec2_type", "|u1"),
            ("rec2_value", "<f4"),
            ("rec2_value_unit", "|u1"),
            ("rec3_type", "|u1"),
            ("rec3_value", "<f4"),
            ("rec3_value_unit", "|u1"),
            ("E_range_min", "<f4"),
            ("E_range_max", "<f4"),
            ("I_range", "|u1"),
            ("I_range_min", "|u1"),
            ("I_range_max", "|u1"),
            ("I_range_init", "|u1"),
            ("auto_rest", "|u1"),
            ("bandwidth", "|u1"),
        ]
    ),
    np.dtype(
        [
            ("ctrl_type", "|u1"),
            ("apply_I/C", "|u1"),
            ("ctrl1_val", "<f4"),
            ("ctrl1_val_unit", "|u1"),
            ("ctrl1_val_vs", "|u1"),
            ("ctrl2_val", "<f4"),
            ("ctrl2_val_unit", "|u1"),
            ("ctrl2_val_vs", "|u1"),
            ("ctrl3_val", "<f4"),
            ("ctrl3_val_unit", "|u1"),
            ("ctrl3_val_vs", "|u1"),
            ("N", "<f4"),
            ("charge/discharge", "|u1"),
            ("ctrl_seq", "<u4"),
            ("ctrl_repeat", "<u4"),
            ("ctrl_trigger", "|u1"),
            ("ctrl_TO_t", "<f4"),
            ("ctrl_TO_t_unit", "|u1"),
            ("ctrl_Nd", "<u4"),
            ("ctrl_Na", "<u4"),
            ("ctrl_corr", "|u1"),
            ("lim_nb", "|u1"),
            ("lim1_type", "|u1"),
            ("lim1_comp", "|u1"),
            ("lim1_Q", "|u1"),
            ("lim1_value", "<f4"),
            ("lim1_value_unit", "|u1"),
            ("lim1_action", "|u1"),
            ("lim1_seq", "<u4"),
            ("lim2_type", "|u1"),
            ("lim2_comp", "|u1"),
            ("lim2_Q", "|u1"),
            ("lim2_value", "<f4"),
            ("lim2_value_unit", "|u1"),
            ("lim2_action", "|u1"),
            ("lim2_seq", "<u4"),
            ("lim3_type", "|u1"),
            ("lim3_comp", "|u1"),
            ("lim3_Q", "|u1"),
            ("lim3_value", "<f4"),
            ("lim3_value_unit", "|u1"),
            ("lim3_action", "|u1"),
            ("lim3_seq", "<u4"),
            ("rec_nb", "|u1"),
            ("rec1_type", "|u1"),
            ("rec1_value", "<f4"),
            ("rec1_value_unit", "|u1"),
            ("rec2_type", "|u1"),
            ("rec2_value", "<f4"),
            ("rec2_value_unit", "|u1"),
            ("rec3_type", "|u1"),
            ("rec3_value", "<f4"),
            ("rec3_value_unit", "|u1"),
            ("E_range_min", "<f4"),
            ("E_range_max", "<f4"),
            ("I_range", "|u1"),
            ("I_range_min", "|u1"),
            ("I_range_max", "|u1"),
            ("I_range_init", "|u1"),
            ("auto_rest", "|u1"),
            ("bandwidth", "|u1"),
        ]
    ),
]

######################### Open Circuit Voltage #########################
def _ocv_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the OCV technique."""
    params = ["tR", "dER/dt"]
    record_match = re.search(r"^record.+", "\n".join(settings))
    if record_match:
        params += ["record"]
    params += ["dER", "dtR", "E_range_min", "E_range_max"]
    return params


_ocv_params_dtypes = [
    np.dtype(
        [
            ("tR", "<f4"),
            ("dER/dt", "<f4"),
            ("record", "|u1"),
            ("dER", "<f4"),
            ("dtR", "<f4"),
            ("E_range_min", "<f4"),
            ("E_range_max", "<f4"),
        ]
    ),
    np.dtype(
        [
            ("tR", "<f4"),
            ("dER/dt", "<f4"),
            ("dER", "<f4"),
            ("dtR", "<f4"),
            ("E_range_min", "<f4"),
            ("E_range_max", "<f4"),
        ]
    ),
]


########### Potentio Electrochemical Impedance Spectroscopy ############
def _peis_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the PEIS technique."""
    params = [
        "sine_mode",
        "E",
        "E_vs",
        "tE",
        "record",
        "dI",
        "dI_unit",
        "dt",
        "fi",
        "fi_unit",
        "ff",
        "ff_unit",
        "Nd",
        "points",
        "spacing",
        "Va",
        "pw",
        "Na",
        "corr",
    ]
    params = _prepend_ns(settings, params)
    lim_nb_match = re.search(r"^lim_nb\s+(?P<val>.+)", "\n".join(settings))
    if lim_nb_match:
        lim_nb = int(max(lim_nb_match["val"].split()))
        params.append("lim_nb")
        for i, __ in enumerate(range(lim_nb), 1):
            limit = [
                f"limit_type{i}",
                f"limit_comp{i}",
                f"limit_value{i}",
                f"limit_unit{i}",
            ]
            params += limit
    params += [
        "E_range_min",
        "E_range_max",
        "I_range",
        "bandwidth",
        "nc_cycles",
        "goto_Ns",
        "nr_cycles",
        "inc_cycle",
    ]
    return params


_peis_params_dtype = np.dtype(
    [
        ("sine_mode", "|u1"),
        ("E", "<f4"),
        ("E_vs", "|u1"),
        ("tE", "<f4"),
        ("record", "|u1"),
        ("dI", "<f4"),
        ("dI_unit", "|u1"),
        ("dt", "<f4"),
        ("fi", "<f4"),
        ("fi_unit", "|u1"),
        ("ff", "<f4"),
        ("ff_unit", "|u1"),
        ("Nd", "<u4"),
        ("points", "|u1"),
        ("spacing", "|u1"),
        ("Va", "<f4"),
        ("pw", "<f4"),
        ("Na", "<u4"),
        ("corr", "|u1"),
        ("lim_nb", "|u1"),
        ("limit_type1", "|u1"),
        ("limit_comp1", "|u1"),
        ("limit_value1", "<f4"),
        ("limit_unit1", "|u1"),
        ("limit_type2", "|u1"),
        ("limit_comp2", "|u1"),
        ("limit_value2", "<f4"),
        ("limit_unit2", "|u1"),
        ("limit_type3", "|u1"),
        ("limit_comp3", "|u1"),
        ("limit_value3", "<f4"),
        ("limit_unit3", "|u1"),
        ("limit_type4", "|u1"),
        ("limit_comp4", "|u1"),
        ("limit_value4", "<f4"),
        ("limit_unit4", "|u1"),
        ("limit_type5", "|u1"),
        ("limit_comp5", "|u1"),
        ("limit_value5", "<f4"),
        ("limit_unit5", "|u1"),
        ("limit_type6", "|u1"),
        ("limit_comp6", "|u1"),
        ("limit_value6", "<f4"),
        ("limit_unit6", "|u1"),
        ("E_range_min", "<f4"),
        ("E_range_max", "<f4"),
        ("I_range", "|u1"),
        ("bandwidth", "|u1"),
        ("nc_cycles", "<u4"),
        ("goto_Ns", "<u4"),
        ("nr_cycles", "<u4"),
        ("inc_cycle", "<u4"),
    ]
)


################################# Wait #################################
def _wait_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the WAIT technique."""
    params = [
        "select",
        "td",
        "from",
        "tech_num",
        "ole_date",
        "ole_time",
        "record",
        "dE",
        "dI",
        "dI_unit",
        "dt",
    ]
    return params


_wait_params_dtype = np.dtype(
    [
        ("select", "|u1"),
        ("td", "<u4"),
        ("from", "|u1"),
        ("tech_num", "|u1"),
        ("ole_date", "<f4"),  # Why the hell would they split this?!
        ("ole_time", "<f4"),
        ("record", "|u1"),
        ("dE", "<f4"),
        ("dI", "<f4"),
        ("dI_unit", "|u1"),
        ("dt", "<f4"),
    ]
)


######################## IR compensation (PEIS) ########################
def _zir_params(settings: list[str]) -> list[str]:
    """Constructs the parameter names for the ZIR technique."""
    params = [
        "E",
        "E_vs",
        "f",
        "f_unit",
        "Va",
        "pw",
        "Na",
        "E_range_min",
        "E_range_max",
        "I_range",
        "bandwidth",
        "comp_level",
        "use_results",
        "comp_mode",
    ]
    return params


_zir_params_dtype = np.dtype(
    [
        ("E", "<f4"),
        ("E_vs", "|u1"),
        ("f", "<f4"),
        ("f_unit", "|u1"),
        ("Va", "<f4"),
        ("pw", "<f4"),
        ("Na", "<u4"),
        ("E_range_min", "<f4"),
        ("E_range_max", "<f4"),
        ("I_range", "|u1"),
        ("bandwidth", "|u1"),
        ("comp_level", "|u1"),
        ("use_results", "|u1"),
        ("comp_mode", "|u1"),
    ]
)


def technique_params(technique: str, settings: list[str]) -> tuple[str, list]:
    """Constructs the parameter names for different techniques.

    Parameters
    ----------
    technique
        The full name of the technique.

    settings
        The list of settings from the start of an .mpt or .mps file.

    Returns
    -------
    tuple[str, list]
        The short technique name and a full list of technique parameter
        names depending on what is present in the file.

    """
    if technique == "Chronoamperometry / Chronocoulometry":
        return "CA", _ca_params(settings)
    if technique == "Chronopotentiometry":
        return "CP", _cp_params(settings)
    if technique == "Cyclic Voltammetry":
        return "CV", _cv_params(settings)
    if technique == "Galvano Electrochemical Impedance Spectroscopy":
        return "GEIS", _geis_params(settings)
    if technique == "Galvanostatic Cycling with Potential Limitation":
        return "GCPL", _gcpl_params(settings)
    if technique == "IR compensation (PEIS)":
        return "ZIR", _zir_params(settings)
    if technique == "Linear Sweep Voltammetry":
        return "LSV", _lsv_params(settings)
    if technique == "Loop":
        return "LOOP", _loop_params(settings)
    if technique == "Modulo Bat":
        return "mb", _mb_params(settings)
    if technique == "Open Circuit Voltage":
        return "OCV", _ocv_params(settings)
    if technique == "Potentio Electrochemical Impedance Spectroscopy":
        return "PEIS", _peis_params(settings)
    if technique == "Wait":
        return "WAIT", _wait_params(settings)
    raise NotImplementedError(f"'{technique}' not implemented.")


# Maps the technique byte to its corresponding dtype.
technique_params_dtypes = {
    0x04: ("GCPL", _gcpl_params_dtype),
    0x06: ("CV", _cv_params_dtype),
    0x0B: ("OCV", _ocv_params_dtypes),
    0x18: ("CA", _ca_params_dtype),
    0x19: ("CP", _cp_params_dtype),
    0x1C: ("WAIT", _wait_params_dtype),
    0x1D: ("PEIS", _peis_params_dtype),
    0x1E: ("GEIS", _geis_params_dtype),
    0x32: ('ZIR', _zir_params_dtype),
    0x6C: ("LSV", _lsv_params_dtype),
    0x7F: ("MB", _mb_params_dtypes),
}
