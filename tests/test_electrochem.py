import json
import os

import numpy as np
import pytest
import xarray
from pathlib import Path

import yadg.extractors
from tests.utils import (
    datagram_from_file,
    datagram_from_input,
    pars_datagram_test,
    standard_datagram_test,
    dg_get_quantity,
    compare_result_dicts,
)


@pytest.mark.parametrize(
    "input, ts",
    [
        (  # ts0 - ca.mpr
            {
                "case": "ca.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 721,
                "point": 0,
                "pars": {
                    "control_V": {
                        "value": 3.0000624e-001,
                        "sigma": 2e-5,
                        "unit": "V",
                    },
                    "uts": {"value": 1556661461.2284908},
                },
            },
        ),
        (  # ts1 - ca.mpt
            {
                "case": "ca.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 721,
                "point": 0,
                "pars": {
                    "control_V": {
                        "value": 3.0000624e-001,
                        "sigma": 2e-5,
                        "unit": "V",
                    },
                    "uts": {"value": 1556661461.2284908},
                },
            },
        ),
        (  # ts2 - cp.mpr
            {
                "case": "cp.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 121,
                "point": 0,
                "pars": {
                    "control_I": {
                        "value": -1.0000000e002,
                        "sigma": 4e-5,
                        "unit": "mA",
                    }
                },
            },
        ),
        (  # ts3 - cp.mpt
            {
                "case": "cp.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 121,
                "point": 0,
                "pars": {
                    "control_I": {
                        "value": -1.0000000e002,
                        "sigma": 4e-5,
                        "unit": "mA",
                    }
                },
            },
        ),
        (  # ts4 - cv.mpr
            {
                "case": "cv.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5103,
                "point": 0,
                "pars": {
                    "control_V": {
                        "value": 2.4814086e000,
                        "sigma": 2e-4,
                        "unit": "V",
                    }
                },
            },
        ),
        (  # ts5 - cv.mpt
            {
                "case": "cv.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5103,
                "point": 0,
                "pars": {
                    "control_V": {
                        "value": 2.4814086e000,
                        "sigma": 2e-4,
                        "unit": "V",
                    }
                },
            },
        ),
        (  # ts6 - gcpl.mpr
            {
                "case": "gcpl.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12057,
                "point": 0,
                "pars": {
                    "control_I": {
                        "value": -1.1000001e-002,
                        "sigma": 760e-12,
                        "unit": "mA",
                    }
                },
            },
        ),
        (  # ts7 - gcpl.mpt
            {
                "case": "gcpl.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12057,
                "point": 0,
                "pars": {
                    "control_I": {
                        "value": -1.1000001e-002,
                        "sigma": 760e-12,
                        "unit": "mA",
                    }
                },
            },
        ),
        (  # ts8 - geis.mpr
            {
                "case": "geis.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 2528,
                "point": 0,
                "pars": {"uts": {"value": 1614849363.9204996}},
            },
        ),
        (  # ts9 - geis.mpt
            {
                "case": "geis.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 2528,
                "point": 0,
                "pars": {"uts": {"value": 1614849363.9204996}},
            },
        ),
        (  # ts10 - lsv.mpr
            {
                "case": "lsv.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1186,
                "point": 0,
                "pars": {
                    "control_V": {
                        "value": -5.6856550e-002,
                        "sigma": 3.0518e-4,
                        "unit": "V",
                    }
                },
            },
        ),
        (  # ts11 - lsv.mpt
            {
                "case": "lsv.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1186,
                "point": 0,
                "pars": {
                    "control_V": {
                        "value": -5.6856550e-002,
                        "sigma": 3.0518e-4,
                        "unit": "V",
                    }
                },
            },
        ),
        (  # ts12 - mb.mpr
            {
                "case": "mb.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1588,
                "point": 0,
                "pars": {
                    "control_I": {
                        "value": 1.0857184e-004,
                        "sigma": 4e-9,
                        "unit": "mA",
                    }
                },
            },
        ),
        (  # ts13 - mb.mpt
            {
                "case": "mb.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1588,
                "point": 0,
                "pars": {
                    "control_I": {
                        "value": 1.0857184e-004,
                        "sigma": 4e-9,
                        "unit": "mA",
                    }
                },
            },
        ),
        (  # ts14 - ocv.mpr
            {
                "case": "ocv.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 602,
                "point": 0,
                "pars": {"uts": {"value": 1579184014.0}},
            },
        ),
        (  # ts15 - ocv.mpt
            {
                "case": "ocv.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 602,
                "point": 0,
                "pars": {"uts": {"value": 1579184014.0}},
            },
        ),
        (  # ts16 - peis.mpr
            {
                "case": "peis.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 32,
                "point": 0,
                "pars": {"uts": {"value": 1614702327.1567264}},
            },
        ),
        (  # ts17 - peis.mpt
            {
                "case": "peis.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 32,
                "point": 0,
                "pars": {"uts": {"value": 1614702327.1567264}},
            },
        ),
        (  # ts18 - zir.mpr
            {
                "case": "zir.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "pars": {"uts": {"value": 1522109455.9886506}},
            },
        ),
        (  # ts19 - zir.mpt
            {
                "case": "zir.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "pars": {"uts": {"value": 1522109455.9886506}},
            },
        ),
        (  # ts20 - mb_67.mpr
            {
                "case": "mb_67.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 33,
                "point": 0,
                "pars": {
                    "uts": {"value": 1670510213.355},
                    "Ewe": {"value": 2.3278546, "unit": "V", "sigma": 7.5e-05},
                },
            },
        ),
        (  # ts21 - mb_67.mpt
            {
                "case": "mb_67.mpt",
                "encoding": "windows-1252",
                "locale": "de_DE.UTF-8",
                "parameters": {"filetype": "eclab.mpt"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 33,
                "point": 0,
                "pars": {
                    "uts": {"value": 1670510213.355},
                    "Ewe": {"value": 2.3278546, "unit": "V", "sigma": 7.5e-05},
                },
            },
        ),
    ],
)
def test_electrochem_from_eclab(input, ts, datadir):
    ret = datagram_from_input(input, "electrochem", datadir, version="5.0")
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)


@pytest.mark.parametrize(
    "input",
    [
        {  # ts0 - wait.mpr
            "case": "wait.mpr",
            "encoding": "windows-1252",
            "parameters": {"filetype": "eclab.mpr"},
        },
        {  # ts1 - wait.mpt
            "case": "wait.mpt",
            "encoding": "windows-1252",
            "parameters": {"filetype": "eclab.mpt"},
        },
    ],
)
def test_electrochem_wait_technique(input, datadir):
    dg = datagram_from_input(input, "electrochem", datadir)
    assert not dg["0"].data_vars, "No data should be present."


@pytest.mark.parametrize(
    "input, refpath",
    [
        (
            {  # ts0 - ca.mpr
                "case": "ca.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            "ca.dg.json",
        ),
        (
            {  # ts1 - ca.mpt
                "case": "ca.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            "ca.dg.json",
        ),
        (
            {  # ts2 - geis.mpr
                "case": "geis.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            "geis.dg.json",
        ),
        (
            {  # ts3 - geis.mpt
                "case": "geis.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            "geis.dg.json",
        ),
    ],
)
def test_electrochem_compare_raw_values(input, refpath, datadir):
    os.chdir(datadir)
    dg = datagram_from_input(input, "electrochem", datadir)
    step = dg["0"]
    with open(refpath, "r") as infile:
        ref = json.load(infile)["steps"][0]["data"]
    for k in step:
        if k == "uts":
            uts = [ts["uts"] for ts in ref]
            np.testing.assert_allclose(step["uts"], uts)
        elif k.endswith("_std_err"):
            continue
        else:
            res = dg_get_quantity(dg, 0, k)
            if isinstance(res, dict):
                n = [ts["raw"][k]["n"] for ts in ref]
                s = [ts["raw"][k]["s"] for ts in ref]
                u = ref[0]["raw"][k]["u"]
                compare_result_dicts(res, {"n": n, "s": s, "u": u})
            else:
                tv = [ts["raw"][k] for ts in ref]
                assert (res == tv).all()


@pytest.mark.parametrize(
    "input, ts",
    [
        (  # ts0 - vsp_ocv without external devices
            {
                "case": "vsp_ocv_wo.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 121,
                "point": 0,
                "pars": {
                    "Ewe": {
                        "value": 0.03291448,
                        "sigma": 0.00015,
                        "unit": "V",
                    },
                    "uts": {"value": 1641938088.5444725},
                },
            },
        ),
        (  # ts1 - vsp_ocv with external devices
            {
                "case": "vsp_ocv_with.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
                "externaldate": {"from": {"utsoffset": 0.0}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 13,
                "point": 12,
                "pars": {
                    "Ewe": {
                        "value": 0.000106005,
                        "sigma": 0.00015,
                        "unit": "V",
                    },
                    "Force": {
                        "value": 162.9350891,
                        "sigma": 0.0165,
                        "unit": "N",
                    },
                    "Temperatur": {
                        "value": 27.77219582,
                        "sigma": 0.00225,
                        "unit": "°C",
                    },
                    "uts": {"value": 53996.920794260455},
                },
            },
        ),
        (  # ts2 - vsp_peis with external devices
            {
                "case": "vsp_peis_with.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
                "externaldate": {"from": {"utsoffset": 0.0}},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 2240,
                "point": 840,
                "pars": {
                    "uts": {"value": 527655.5950297173},
                },
            },
        ),
    ],
)
def test_electrochem_vsp_3e(input, ts, datadir):
    ret = datagram_from_input(input, "electrochem", datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts, atol=1e-8)


@pytest.mark.parametrize(
    "infile, ts",
    [
        (
            "ts0_electrochem_tomato.yml",
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 51,
                "point": 9,
                "pars": {
                    "uts": {"value": 1650490355.3152814},
                    "Ewe": {"value": 4.2000856399, "sigma": 0.00015, "unit": "V"},
                    "I": {"value": 0.0044998624, "sigma": 4e-7, "unit": "A"},
                },
            },
        ),
    ],
)
def test_electrochem_tomato(infile, ts, datadir):
    ret = datagram_from_file(infile, datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)


@pytest.mark.parametrize(
    "infile, outfile",
    [
        ("issue_61_Irange_65.mpr", "issue_61.nc"),
        ("issue_61_Irange_65.mpt", "issue_61.nc"),
    ],
)
def test_electrochem_bugs(infile, outfile, datadir):
    os.chdir(datadir)
    if infile.endswith("mpr"):
        filetype = "biologic-mpr"
    elif infile.endswith("mpt"):
        filetype = "biologic-mpt"
    else:
        assert False, "unknown filetype"
    ret = yadg.extractors.extract(filetype=filetype, path=Path(infile))
    ref = xarray.open_dataset(outfile, engine="h5netcdf")
    # ret.to_netcdf(outfile, engine="h5netcdf")
    assert ret["uts"].equals(ref["uts"])
    for k in ret.data_vars:
        if k.endswith("_std_err"):
            continue
        elif ret[k].dtype.kind in {"O", "S", "U"}:
            assert ret[k].equals(ref[k])
        else:
            np.testing.assert_allclose(ret[k], ref[k], equal_nan=True)
