import json
import math
import os

import numpy as np
import pytest

from tests.utils import (
    datagram_from_file,
    datagram_from_input,
    pars_datagram_test,
    standard_datagram_test,
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
                    "control_V/I": {
                        "value": -1.1000001e-002,
                        "sigma": 3.0518e-4,
                        "unit": "V/mA",
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
                    "control_V/I": {
                        "value": -1.1000001e-002,
                        "sigma": 3.0518e-4,
                        "unit": "V/mA",
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
                "nrows": 61,
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
                "nrows": 61,
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
                    "control_V/I": {
                        "value": 1.0857184e-004,
                        "sigma": 3.0518e-4,
                        "unit": "V/mA",
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
                    "control_V/I": {
                        "value": 1.0857184e-004,
                        "sigma": 3.0518e-4,
                        "unit": "V/mA",
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
                "nrows": 1,
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
                "nrows": 1,
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
    ],
)
def test_datagram_from_eclab(input, ts, datadir):
    ret = datagram_from_input(input, "electrochem", datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - wait.mpr
                "case": "wait.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            "ca_data.json",
        ),
        (
            {  # ts1 - wait.mpt
                "case": "wait.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            "ca_data.json",
        ),
    ],
)
def test_datagram_wait_technique(input, ts, datadir):
    ret = datagram_from_input(input, "electrochem", datadir)
    assert not ret["steps"][0]["data"], "No data should be present."


@pytest.mark.parametrize(
    "input, refpath",
    [
        (
            {  # ts0 - ca.mpr
                "case": "ca.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            "ca_data.json",
        ),
        (
            {  # ts1 - ca.mpt
                "case": "ca.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            "ca_data.json",
        ),
    ],
)
def test_compare_raw_values_time_series(input, refpath, datadir):
    os.chdir(datadir)
    with open(refpath, "r") as infile:
        ref = json.load(infile)
    ret = datagram_from_input(input, "electrochem", datadir)
    ret = ret["steps"][0]["data"]
    with open(refpath, "w") as of:
        json.dump(ret, of)
    for ts_ret, ts_ref in zip(ret, ref):
        for key in ts_ret["raw"].keys():
            if isinstance(ts_ref["raw"][key], dict):
                for i in ["n", "s"]:
                    assert np.allclose(
                        ts_ref["raw"][key][i], ts_ret["raw"][key][i], equal_nan=True
                    )
            else:
                assert ts_ref["raw"][key] == ts_ret["raw"][key]


@pytest.mark.parametrize(
    "input, refpath",
    [
        (
            {  # ts0 - geis.mpr
                "case": "geis.mpr",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpr"},
            },
            "geis_data.json",
        ),
        (
            {  # ts1 - geis.mpt
                "case": "geis.mpt",
                "encoding": "windows-1252",
                "parameters": {"filetype": "eclab.mpt"},
            },
            "geis_data.json",
        ),
    ],
)
def test_compare_raw_values_eis_traces(input, refpath, datadir):
    os.chdir(datadir)
    with open(refpath, "r") as infile:
        ref = json.load(infile)
    ret = datagram_from_input(input, "electrochem", datadir)
    ret = ret["steps"][0]["data"][0]["raw"]["traces"]
    with open(refpath, "w") as of:
        json.dump(ret, of)
    for n, trace in ret.items():
        for ax in trace:
            if isinstance(ref[n][ax], dict):
                for i in ["n", "s"]:
                    assert np.allclose(ref[n][ax][i], ret[n][ax][i], equal_nan=True)
            else:
                assert ref[n][ax] == ret[n][ax]


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
                        "value": 0.0329145,
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
                        "value": 0.0001060,
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
                "nrows": 32,
                "point": 12,
                "pars": {
                    "uts": {"value": 527655.5950297173},
                },
            },
        ),
    ],
)
def test_vsp_3e(input, ts, datadir):
    ret = datagram_from_input(input, "electrochem", datadir)
    standard_datagram_test(ret, ts)
    pars_datagram_test(ret, ts)


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
    "input",
    [
        {"case": "peis.mpr", "parameters": {"filetype": "eclab.mpr"}},
        {
            "case": "peis.mpt",
            "encoding": "windows-1252",
            "parameters": {"filetype": "eclab.mpt"},
        },
        {"case": "geis.mpr", "parameters": {"filetype": "eclab.mpr"}},
        {
            "case": "geis.mpt",
            "encoding": "windows-1252",
            "parameters": {"filetype": "eclab.mpt"},
        },
    ],
)
@pytest.mark.parametrize("transpose", [True, False])
def test_electrochem_transpose(input, transpose, datadir):
    input["parameters"]["transpose"] = transpose
    ret = datagram_from_input(input, "electrochem", datadir, version="4.2")
    if transpose and input["case"].startswith("p"):
        nrows = 1
    elif input["case"].startswith("p"):
        nrows = 32
    if transpose and input["case"].startswith("g"):
        nrows = 61
    elif input["case"].startswith("g"):
        nrows = 2528
    ts = {"nsteps": 1, "step": 0, "nrows": nrows}
    standard_datagram_test(ret, ts)
    if transpose:
        assert all(["traces" in ts["raw"] for ts in ret["steps"][0]["data"]])
    else:
        assert all(["traces" not in ts["raw"] for ts in ret["steps"][0]["data"]])
