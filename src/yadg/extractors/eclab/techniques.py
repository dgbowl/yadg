"""
**techniques**: Parameters for implemented techniques.
------------------------------------------------------

Implemented techniques:

    - CA - Chronoamperometry / Chronocoulometry
    - CP - Chronopotentiometry
    - CV - Cyclic Voltammetry
    - CVA - Cyclic Voltammetry Advanced
    - GCPL - Galvanostatic Cycling with Potential Limitation
    - GEIS - Galvano Electrochemical Impedance Spectroscopy
    - LOOP - Loop
    - LSV - Linear Sweep Voltammetry
    - MB - Modulo Bat
    - OCV - Open Circuit Voltage
    - PEIS - Potentio Electrochemical Impedance Spectroscopy
    - WAIT - Wait
    - ZIR - IR compensation (PEIS)
    - MP - Modular Potentio
    - CoV - Constant Voltage

The module also implements resolution determination for parameters of techniques,
in :func:`get_resolution`.

"""

import numpy as np
from math import sqrt
from typing import Union, Any
import bisect
import logging

logger = logging.getLogger(__name__)


# ~~~~~~~~~~~~~ Chronoamperometry / Chronocoulometry ~~~~~~~~~~~~~
_ca_params_dtypes = [
    (
        np.dtype(
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
        ),
        {"10.40"},
    ),
    (
        np.dtype(
            [
                ("Ei", "<f4"),
                ("Ei_vs", "|u4"),
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
        ),
        {"11.50"},
    ),
]


# ~~~~~~~~~~~~~ Chronopotentiometry ~~~~~~~~~~~~~
_cp_params_dtypes = [
    (
        np.dtype(
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
        ),
        {"10.40"},
    ),
    (
        np.dtype(
            [
                ("Is", "<f4"),
                ("Is_unit", "|u1"),
                ("Is_vs", "|u4"),
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
        ),
        {"11.50"},
    ),
]


# ~~~~~~~~~~~~~ Cyclic Voltammetry ~~~~~~~~~~~~~
_cv_params_dtypes = [
    (
        np.dtype(
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
        ),
        {"10.40", "11.50"},
    )
]


# ~~~~~~~~~~~~~ Cyclic Voltammetry Advanced ~~~~~~~~~~~~~
_cva_params_dtypes = [
    (
        np.dtype(
            [
                ("Ei", "<f4"),
                ("Ei_vs", "|u1"),
                ("ti", "<f4"),
                ("dti", "<f4"),
                ("dE/dt", "<f4"),
                ("dE/dt_unit", "|u1"),
                ("E1", "<f4"),
                ("E1_vs", "|u1"),
                ("t1", "<f4"),
                ("dt1", "<f4"),
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
                ("t2", "<f4"),
                ("dt2", "<f4"),
                ("nc_cycles", "<u4"),
                ("nr", "|u1"),
                ("reverse_scan", "|u1"),
                ("Ef", "<f4"),
                ("Ef_vs", "|u1"),
                ("tf", "<f4"),
                ("dtf", "<f4"),
            ]
        ),
        {"10.40", "11.50"},
    )
]


# ~~~~~~~~~~~~~ Galvanostatic Cycling with Potential Limitation ~~~~~~~~~~~~~
_gcpl_params_dtypes = [
    (
        np.dtype(
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
        ),
        {"10.40"},
    ),
    (
        np.dtype(
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
                ("delta SoC", "<f4"),
                ("tR", "<f4"),
                ("dER/dt", "<f4"),
                ("dER", "<f4"),
                ("dtR", "<f4"),
                ("EL", "<f4"),
                ("goto_Ns", "<u4"),
                ("nc_cycles", "<u4"),
            ]
        ),
        {"10.40"},
    ),
    (
        np.dtype(
            [
                ("set_I/C", "|u1"),
                ("Is", "<f4"),
                ("Is_unit", "|u1"),
                ("Is_vs", "|u4"),
                ("N", "<f4"),
                ("I_sign", "|u4"),
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
                ("delta SoC", "<f4"),
                ("tR", "<f4"),
                ("dER/dt", "<f4"),
                ("dER", "<f4"),
                ("dtR", "<f4"),
                ("EL", "<f4"),
                ("goto_Ns", "u4"),
                ("nc_cycles", "u4"),
            ]
        ),
        {"11.50"},
    ),
]


# ~~~~~~~~~~~~~ Galvano Electrochemical Impedance Spectroscopy ~~~~~~~~~~~~~
_geis_params_dtype = [
    (
        np.dtype(
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
        ),
        {"10.40"},
    ),
    (
        np.dtype(
            [
                ("sine_mode", "|u1"),
                ("Is", "<f4"),
                ("Is_unit", "|u1"),
                ("Is_vs", "|u4"),
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
        ),
        {"11.50"},
    ),
]


# ~~~~~~~~~~~~~ Linear Sweep Voltammetry ~~~~~~~~~~~~~
_lsv_params_dtype = [
    (
        np.dtype(
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
        ),
        {"10.40", "11.50"},
    )
]


# ~~~~~~~~~~~~~ Modulo Bat ~~~~~~~~~~~~~
_mb_params_dtypes = [
    (
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
        {"10.40"},
    ),
    (
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
        {"10.40"},
    ),
    (
        np.dtype(
            [
                ("ctrl_type", "|u1"),
                ("apply_I/C", "|u1"),
                ("current/potential", "|u1"),
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
        {"10.40"},
    ),
    (
        np.dtype(
            [
                ("ctrl_type", "|u2"),
                ("apply_I/C", "|u2"),
                ("current/potential", "|u2"),
                ("ctrl1_val", "<f4"),
                ("ctrl1_val_unit", "|u1"),
                ("ctrl1_val_vs", "|u4"),
                ("ctrl2_val", "<f4"),
                ("ctrl2_val_unit", "|u1"),
                ("ctrl2_val_vs", "|u4"),
                ("ctrl3_val", "<f4"),
                ("ctrl3_val_unit", "|u1"),
                ("ctrl3_val_vs", "|u4"),
                ("N", "<f4"),
                ("charge/discharge", "|u1"),
                ("charge/discharge_1", "|u2"),
                ("apply_I/C_1", "|u4"),
                ("N1", "<f4"),
                ("ctrl4_val", "<f4"),
                ("ctrl4_val_unit", "|u2"),
                ("ctrl5_val", "<f4"),
                ("ctrl5_val_unit", "|u2"),
                ("ctrl_tM", "|u4"),
                ("ctrl_seq", "|u4"),
                ("ctrl_repeat", "|u1"),
                ("ctrl_trigger", "|u4"),
                ("ctrl_TO_t", "<f4"),
                ("ctrl_TO_t_unit", "|u1"),
                ("ctrl_Nd", "|u4"),
                ("ctrl_Na", "|u1"),
                ("ctrl_corr", "|u4"),
                ("lim_nb", "|u4"),
                ("lim1_type", "|u1"),
                ("lim1_comp", "|u1"),
                ("lim1_Q", "|u1"),
                ("lim1_value", "<f4"),
                ("lim1_value_unit", "|u1"),
                ("lim1_action", "|u1"),
                ("lim1_seq", "|u4"),
                ("lim2_type", "|u1"),
                ("lim2_comp", "|u1"),
                ("lim2_Q", "|u1"),
                ("lim2_value", "<f4"),
                ("lim2_value_unit", "|u1"),
                ("lim2_action", "|u1"),
                ("lim2_seq", "|u4"),
                ("lim3_type", "|u1"),
                ("lim3_comp", "|u1"),
                ("lim3_Q", "|u1"),
                ("lim3_value", "<f4"),
                ("lim3_value_unit", "|u1"),
                ("lim3_action", "|u1"),
                ("lim3_seq", "|u4"),
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
                ("auto_rest", "|u4"),
                ("bandwidth", "|u1"),
            ]
        ),
        {"11.50"},
    ),
]


# ~~~~~~~~~~~~~ Open Circuit Voltage ~~~~~~~~~~~~~
_ocv_params_dtypes = [
    (
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
        {"10.40", "11.50"},
    ),
    (
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
        {"10.40", "11.50"},
    ),
]


# ~~~~~~~~~~~~~ Potentio Electrochemical Impedance Spectroscopy ~~~~~~~~~~~~~
_peis_params_dtypes = [
    (
        np.dtype(
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
        ),
        {"10.40"},
    ),
    (
        np.dtype(
            [
                ("sine_mode", "|u4"),
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
        ),
        {"11.50"},
    ),
]


# ~~~~~~~~~~~~~ Wait ~~~~~~~~~~~~~
_wait_params_dtypes = [
    (
        np.dtype(
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
        ),
        {"10.40", "11.50"},
    )
]


# ~~~~~~~~~~~~~ IR compensation (PEIS) ~~~~~~~~~~~~~
_zir_params_dtypes = [
    (
        np.dtype(
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
        ),
        {"10.40", "11.50"},
    )
]

# ~~~~~~~~~~~~~ Modular Potentio ~~~~~~~~~~~~~
_mp_params_dtypes = [
    (
        np.dtype(
            [
                ("Mode", "<u4"),
                ("tR", "<f4"),
                ("dER/dt", "<f4"),
                ("dER", "<f4"),
                ("dtR", "<f4"),
                ("Es", "<f4"),
                ("Es_vs", "<u4"),
                ("ts", "<f4"),
                ("dE/dt", "<f4"),
                ("dE/dt_unit", "|u1"),
                ("Ei", "<f4"),
                ("Ei_vs", "<u4"),
                ("Ef", "<f4"),
                ("Ef_vs", "<u4"),
                ("E_range_min", "<f4"),
                ("E_range_max", "<f4"),
                ("I_range", "|u1"),
                ("I_range_min", "|u1"),
                ("I_range_max", "|u1"),
                ("I_range_init", "|u1"),
                ("bandwidth", "|u1"),
                ("record", "|u1"),
                ("dIp", "<f4"),
                ("dIp_unit", "|u1"),
                ("dQp", "<f4"),
                ("dQp_unit", "|u1"),
                ("dtp", "<f4"),
                ("dts", "<f4"),
                ("step_percent", "|u1"),
                ("N", "|u1"),
                ("dQM", "<f4"),
                ("dQM_unit", "<u4"),
                ("Imax", "<f4"),
                ("Imax_unit", "|u1"),
                ("Imin", "<f4"),
                ("Imin_unit", "|u1"),
                ("goto_Ns", "|u4"),
                ("nc_cycles", "<u4"),
            ]
        ),
        {"11.50"},
    )
]

# ~~~~~~~~~~~~~ Constant Voltage ~~~~~~~~~~~~~
_cov_params_dtypes = [
    (
        np.dtype(
            [
                ("tR", "<f4"),
                ("dER/dt", "<f4"),
                ("dER", "<f4"),
                ("dtR", "<f4"),
                ("Ei", "<f4"),
                ("Ei_vs", "<u4"),
                ("ti", "<f4"),
                ("Imax", "<f4"),
                ("Imax_unit", "|u1"),
                ("Imin", "<f4"),
                ("Imin_unit", "|u1"),
                ("dQM", "<f4"),
                ("dQM_unit", "<u4"),
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
                ("bandwidth", "|u1"),
                ("goto_Ns", "<u4"),
                ("nc_cycles", "<u4"),
            ]
        ),
        {"11.50"},
    )
]

# ~~~~~~~~~~~~~ Constant Current ~~~~~~~~~~~~~
_coc_params_dtypes = [
    (
        np.dtype(
            [
                ("tR", "<f4"),
                ("dER/dt", "<f4"),
                ("dER", "<f4"),
                ("dtR", "<f4"),
                ("Is", "<f4"),
                ("Is_unit", "|u1"),
                ("Is_vs", "|u4"),
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
        ),
        {"11.50"},
    )
]


# Maps the technique byte to its corresponding dtype.
technique_params_dtypes = {
    0x04: ("GCPL", _gcpl_params_dtypes),
    0x06: ("CV", _cv_params_dtypes),
    0x0B: ("OCV", _ocv_params_dtypes),
    0x16: ("MP", _mp_params_dtypes),
    0x18: ("CA", _ca_params_dtypes),
    0x19: ("CP", _cp_params_dtypes),
    0x1C: ("WAIT", _wait_params_dtypes),
    0x1D: ("PEIS", _peis_params_dtypes),
    0x1E: ("GEIS", _geis_params_dtype),
    0x30: ("CV", _cv_params_dtypes),
    0x32: ("ZIR", _zir_params_dtypes),
    0x33: ("CVA", _cva_params_dtypes),
    0x6C: ("LSV", _lsv_params_dtype),
    0x75: ("coV", _cov_params_dtypes),
    0x76: ("coC", _coc_params_dtypes),
    0x77: ("GCPL", _gcpl_params_dtypes),
    0x7F: ("MB", _mb_params_dtypes),
}

param_map = {
    "I_range": (
        ("10 mA", 1, 1e-2),
        ("100 µA", 2, 1e-4),
        ("1 µA", 3, 1e-6),
        ("2 A", 4, 2.0),
        ("1 A", 5, 1.0),
        ("5 A", 6, 5.0),
        ("10 A", 7, 10.0),
        ("20 A", 8, 20.0),
        ("1 A", 9, 1.0),
        ("100 mA", 10, 1e-1),
        ("10 mA", 11, 1e-2),
        ("1 mA", 12, 1e-3),
        ("100 µA", 13, 1e-4),
        ("10 µA", 14, 1e-5),
        ("Auto", 15, None),  # Auto I Range
        ("100 mA", 16, 1e-1),
        ("10 mA", 17, 1e-2),
        ("1 mA", 18, 1e-3),
        ("100 µA", 19, 1e-4),
        ("100 µA", 20, 1e-4),
        ("10 µA", 21, 1e-5),
        ("1 µA", 22, 1e-6),
        ("100 nA", 23, 1e-7),
        ("10 nA", 24, 1e-8),
        ("1 nA", 25, 1e-9),
        ("80 A", 26, 80.0),
        ("4 A", 27, 4.0),
        ("PAC", 28, None),  # PAC I Range
        ("4 A", 29, 4.0),
        ("100 µA", 30, 1e-4),
        ("10 µA", 31, 1e-5),
        ("1 µA", 32, 1e-6),
        ("100 nA", 33, 1e-7),
        ("10 nA", 34, 1e-8),
        ("1 nA", 35, 1e-9),
        ("8 A", 36, 8.0),
        ("1 A", 37, 1.0),
        ("100 mA", 38, 1e-1),
        ("10 mA", 39, 1e-2),
        ("1 mA", 40, 1e-3),
        ("100 µA", 41, 1e-4),
        ("10 µA", 42, 1e-5),
        ("1 µA", 43, 1e-6),
        ("100 nA", 44, 1e-7),
        ("10 nA", 45, 1e-8),
        ("50 A", 46, 50.0),
        ("5 A", 47, 5.0),
        ("100 A", 48, 1e2),
        ("150 A", 49, 1.5e2),
        ("1 A", 50, 1.0),
        ("4 A", 51, 4.0),
        ("100 µA", 52, 1e-4),
        ("10 µA", 53, 1e-5),
        ("1 µA", 54, 1e-6),
        ("100 nA", 55, 1e-7),
        ("10 nA", 56, 1e-8),
        ("1 nA", 57, 1e-9),
        ("100 pA", 58, 1e-10),
        ("10 pA", 59, 1e-11),
        ("1 pA", 60, 1e-12),
        ("5 A", 61, 5.0),
        ("10 A", 62, 10.0),
        ("20 A", 63, 20.0),
        ("40 A", 64, 40.0),
        ("10 A", 65, 10.0),
        ("2 A", 66, 2.0),
        ("8 A", 67, 8.0),
        ("12 A", 68, 12.0),
        ("16 A", 69, 16.0),
        ("20 A", 70, 20.0),
        ("24 A", 71, 24.0),
        ("28 A", 72, 28.0),
        ("32 A", 73, 32.0),
        ("36 A", 74, 36.0),
        ("40 A", 75, 40.0),
        ("44 A", 76, 44.0),
        ("48 A", 77, 48.0),
        ("52 A", 78, 52.0),
        ("56 A", 79, 56.0),
        ("60 A", 80, 60.0),
        ("64 A", 81, 64.0),
        ("20 A", 82, 20.0),
        ("30 A", 83, 30.0),
        ("40 A", 84, 40.0),
        ("50 A", 85, 50.0),
        ("60 A", 86, 60.0),
        ("70 A", 87, 70.0),
        ("80 A", 88, 80.0),
        ("90 A", 89, 90.0),
        ("100 A", 90, 100.0),
        ("110 A", 91, 110.0),
        ("120 A", 92, 120.0),
        ("130 A", 93, 130.0),
        ("140 A", 94, 140.0),
        ("150 A", 95, 150.0),
        ("160 A", 96, 160.0),
        ("4 A", 97, 4.0),
        ("6 A", 98, 6.0),
        ("8 A", 99, 8.0),
        ("10 A", 100, 10.0),
        ("12 A", 101, 12.0),
        ("14 A", 102, 14.0),
        ("16 A", 103, 16.0),
        ("18 A", 104, 18.0),
        ("20 A", 105, 20.0),
        ("22 A", 106, 22.0),
        ("24 A", 107, 24.0),
        ("26 A", 108, 26.0),
        ("28 A", 109, 28.0),
        ("30 A", 110, 30.0),
        ("32 A", 111, 32.0),
        ("10 A", 112, 10.0),
        ("1 A", 113, 1.0),
        ("100 mA", 114, 1e-1),
        ("10 mA", 115, 1e-2),
        ("1 mA", 116, 1e-3),
        ("100 µA", 117, 1e-4),
        ("10 µA", 118, 1e-5),
        ("20 A", 119, 20.0),
        ("40 A", 120, 40.0),
        ("80 A", 121, 80.0),
        ("Auto Limited", 122, None),  # Auto Limited I Range
        ("Unset", 123, None),  # Unset I Range
        ("300 mA", 124, 0.3),
        ("3 A", 125, 3.0),
        ("30 A", 126, 30.0),
        ("60 A", 127, 60.0),
        ("90 A", 128, 90.0),
        ("120 A", 129, 120.0),
        ("150 A", 130, 150.0),
        ("180 A", 131, 180.0),
        ("210 A", 132, 210.0),
        ("240 A", 133, 240.0),
        ("270 A", 134, 270.0),
        ("300 A", 135, 300.0),
        ("330 A", 136, 330.0),
        ("360 A", 137, 360.0),
        ("390 A", 138, 390.0),
        ("420 A", 139, 420.0),
        ("450 A", 140, 450.0),
        ("480 A", 141, 480.0),
        ("50 A", 142, 50.0),
        ("100 A", 143, 100.0),
        ("150 A", 144, 150.0),
        ("200 A", 145, 200.0),
        ("200 A", 146, 200.0),
        ("400 A", 147, 400.0),
        ("600 A", 148, 600.0),
        ("800 A", 149, 800.0),
        ("50 A", 150, 50.0),
        ("100 A", 151, 100.0),
        ("150 A", 152, 150.0),
        ("200 A", 153, 200.0),
        ("1 A", 154, 1.0),
        ("2 A", 155, 2.0),
        ("3 A", 156, 3.0),
        ("4 A", 157, 4.0),
        ("5 A", 158, 5.0),
        ("6 A", 159, 6.0),
        ("7 A", 160, 7.0),
        ("8 A", 161, 8.0),
        ("9 A", 162, 9.0),
        ("10 A", 163, 10.0),
        ("11 A", 164, 11.0),
        ("12 A", 165, 12.0),
        ("13 A", 166, 13.0),
        ("14 A", 167, 14.0),
        ("15 A", 168, 15.0),
        ("16 A", 169, 16.0),
        ("50 A", 170, 50.0),
        ("100 A", 171, 100.0),
        ("150 A", 172, 150.0),
        ("200 A", 173, 200.0),
        ("50 A", 174, 50.0),
        ("100 A", 175, 100.0),
        ("150 A", 176, 150.0),
        ("200 A", 177, 200.0),
        ("1 A", 178, 1.0),
        ("2 A", 179, 2.0),
        ("3 A", 180, 3.0),
        ("4 A", 181, 4.0),
        ("5 A", 182, 5.0),
        ("6 A", 183, 6.0),
        ("7 A", 184, 7.0),
        ("8 A", 185, 8.0),
        ("9 A", 186, 9.0),
        ("10 A", 187, 10.0),
        ("11 A", 188, 11.0),
        ("12 A", 189, 12.0),
        ("13 A", 190, 13.0),
        ("14 A", 191, 14.0),
        ("15 A", 192, 15.0),
        ("16 A", 193, 16.0),
        ("Auto", None, None),
    ),
    "Is_unit": (
        ("A", 0),  # guess
        ("mA", 1),
        ("µA", 2),
        ("nA", 3),  # guess
        ("pA", 4),  # guess
    ),
    "set_I/C": (
        ("I", 0),
        ("C", 1),  # guess
    ),
    "apply_I/C": (
        ("I", 0),
        ("C", 1),
    ),
}


def param_from_key(
    param: str, key: Union[int, str], to_str: bool = True
) -> Union[str, float]:
    """
    Convert a supplied key of a certain parameter to its string or float value.

    The function uses the map defined in ``param_map`` to convert between the
    entries in the tuples, which contain the :class:`str` value of the parameter
    (present in ``.mpt`` files), the :class:`int` value of the parameter (present
    in ``.mpr`` files), and the corresponding :class:`float` value in SI units.

    Parameters
    ----------
    param
        The name of the parameter, a key within the ``param_map``. If ``param``
        is not present in ``param_map``, the supplied key is returned back.

    key
        The key of the parameter that is to be converted to a different representation.

    to_str
        A switch between :class:`str` and :class:`float` output.

    Returns
    -------
    key: Union[str, float, int]
        The key converted to the requested format.

    """
    ii = 1 if isinstance(key, int) else 0
    if param in param_map:
        for i in param_map[param]:
            if i[ii] == key:
                if to_str:
                    return i[0]
                else:
                    return i[2]
        raise ValueError(f"element '{key}' for parameter '{param}' not understood.")
    return key


def dev_VI(name: str, value: float, unit: str, Erange: float, Irange: float) -> float:
    """
    Function that returns the resolution of a voltage or current based on its name,
    value, E-range and I-range.

    The values used here are hard-coded from VMP-3 potentiostats.

    """
    if name in {"control_V"} and unit in {"V"}:
        # VMP-3: bisect function between 5 µV and 300 µV, as the
        # voltage is stored in a 16-bit int.
        if Erange >= 20.0:
            return 305.18e-6
        else:
            res = [5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 150e-6, 200e-6, 300e-6, 305.18e-6]
            i = bisect.bisect_right(res, Erange / np.iinfo(np.uint16).max)
            return res[i]
    elif name in {"control_I"} and unit in {"mA"}:
        # VMP-3: 0.004% of FSR, 760 µV at 10 µA I-range
        return max(Irange * 0.004 / 100, 760e-12)
    elif unit in {"V", "mV", "μV"}:
        # VMP-3: 0.0015% of FSR, 75 µV minimum
        return max(Erange * 0.0015 / 100, 75e-6)
    elif unit in {"A", "mA", "µA", "nA", "pA"}:
        # VMP-3: 0.004% of FSR
        return Irange * 0.004 / 100
    else:
        raise RuntimeError(f"Unknown quantity {name!r} passed with unit {unit!r}.")


def dev_derived(
    name: str,
    unit: str,
    val: float,
    rtol_I: float,
    rtol_V: float,
    rtol_VI: float,
) -> float:
    """
    Function that returns the resolution of a derived quantity based on its unit,
    value, and the relative error in the current and voltage.

    The values used here are hard-coded from VMP-3 potentiostats.

    """
    if unit in {"V", "mV", "µV"}:
        return val * rtol_V
    elif unit in {"A", "mA", "µA", "nA", "pA"}:
        return val * rtol_I
    elif unit in {"Hz"}:
        # VMP-3: using accuracy: 1% of value
        return val * 0.01
    elif unit in {"deg"}:
        # VMP-3: using accuracy: 1 degree
        return 1.0
    elif unit in {"Ω", "S", "W"}:
        # [Ω] = [V]/[A];
        # [S] = [A]/[V];
        # [W] = [A]*[V];
        return val * rtol_VI
    elif unit in {"C"}:
        # [C] = [A]*[s];
        return val * rtol_I
    elif unit in {"mA·h"}:
        # [A·h] = [A]*[h]
        return val * rtol_I
    elif unit in {"W·h"}:
        # [W·h] = [A]*[V]*[h]
        return val * rtol_VI
    elif unit in {"µF", "nF"}:
        # [F] = [C]/[V] = [A]*[s]/[V]
        return val * rtol_VI
    elif unit in {"Ω·cm", "Ω·m"}:
        # [Ω·m] = [Ω]*[m] = [V]*[m]/[A]
        return val * rtol_VI
    elif unit in {"mS/cm", "S/cm", "mS/m", "S/m"}:
        # [S/m] = 1 / ([Ω]*[m]) = [A] / ([V]*[m])
        return val * rtol_VI
    elif unit in {"s"}:
        # Based on the EC-Lib documentation,
        # 50 us is a safe upper limit for timebase
        return 50e-6
    elif unit in {"%"}:
        return 0.1
    elif name in {"Re(M)", "Im(M)", "|M|"}:
        return float("nan")
    elif name in {"Tan(Delta)"}:
        return float("nan")
    elif name in {"Re(Permittivity)", "Im(Permittivity)", "|Permittivity|"}:
        # εr = ε/ε0
        # ε -> [F]/[m] = [A]*[s]/[V]
        return val * rtol_VI
    else:
        raise RuntimeError(
            f"Could not get resolution of quantity {name!r} with unit {unit!r}."
        )


def get_devs(
    vals: dict[str, Any],
    units: dict[str, str],
    Erange: float,
    Irange: float,
    devs: dict[str, float] = None,
) -> dict[str, float]:
    rtol_V = 0.0
    rtol_I = 0.0
    if devs is None:
        devs = {}
    for col in ["<Ewe>", "<I>", "Ewe", "I", "control_I", "control_V"]:
        val = vals.get(col)
        unit = units.get(col)
        if val is None:
            continue
        devs[col] = max(
            dev_VI(col, abs(val), unit, Erange, Irange),
            devs.get(col, float("nan")),
        )
        if val == 0.0:
            continue
        elif col in {"Ewe", "<Ewe>"}:
            rtol_V = min(max(rtol_V, devs[col] / abs(val)), 1.0)
        elif col in {"I", "<I>"}:
            rtol_I = min(max(rtol_I, devs[col] / abs(val)), 1.0)

    r_sqrtVI = sqrt(rtol_I**2 + rtol_V**2)

    for col, val in vals.items():
        if col in {"<Ewe>", "<I>", "Ewe", "I", "control_I", "control_V"}:
            continue
        elif col.startswith("unknown_"):
            continue
        unit = units.get(col)
        if isinstance(val, float):
            if col in devs:
                devs[col] = max(
                    devs[col],
                    dev_derived(col, unit, abs(val), rtol_I, rtol_V, r_sqrtVI),
                )
            else:
                devs[col] = dev_derived(col, unit, abs(val), rtol_I, rtol_V, r_sqrtVI)

    return devs
