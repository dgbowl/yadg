import pytest
import os
import json
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
    dg_get_quantity,
)


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - datasc parse & integration from file
                "folders": ["."],
                "prefix": "2019-12-03",
                "suffix": "dat.asc",
                "parameters": {"tracetype": "ezchrom.asc"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "polyarc+TCD_PK_09b.met",
                "point": 1,
                "test": {
                    "0": {
                        "i": 1000,
                        "elution_time": {"n": 100.002, "s": 0.100002, "u": "s"},
                        "signal": {"n": 2.085281, "s": 0.000130, "u": "pA"},
                    },
                    "1": {
                        "i": 1000,
                        "elution_time": {"n": 100.002, "s": 0.100002, "u": "s"},
                        "signal": {"n": 55.892435, "s": 0.000130, "u": "V"},
                    },
                },
            },
        ),
        (
            {  # ts1 - chromtab parse
                "folders": ["."],
                "prefix": "CHROMTAB",
                "suffix": "CSV",
                "parameters": {"tracetype": "agilent.csv"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 3,
                "method": None,
                "point": 0,
                "test": {
                    "TCD1A.ch": {
                        "i": 10,
                        "elution_time": {"n": 2.15999999, "s": 0.06, "u": "s"},
                        "signal": {"n": 488830.0, "s": 0.001, "u": None},
                    },
                    "FID2B.ch": {
                        "i": 10,
                        "elution_time": {"n": 2.15999999, "s": 0.06, "u": "s"},
                        "signal": {"n": 42430.0, "s": 0.001},
                    },
                },
            },
        ),
        (
            {  # ts2 - fusion json parse
                "folders": ["."],
                "prefix": "",
                "suffix": "fusion-data",
                "parameters": {"tracetype": "fusion.json"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 5,
                "method": "AS_Cal_20210702",
                "point": 4,
                "test": {
                    "moduleA:tcd": {
                        "i": 100,
                        "elution_time": {"n": 2.0, "s": 0.02, "u": "s"},
                        "signal": {"n": 1566.0, "s": 1.0, "u": None},
                    },
                    "moduleB:tcd": {
                        "i": 100,
                        "elution_time": {"n": 2.0, "s": 0.02, "u": "s"},
                        "signal": {"n": -1412.0, "s": 1.0},
                    },
                },
            },
        ),
        (
            {  # ts3 - fusion zip parse
                "folders": ["."],
                "prefix": "",
                "suffix": "zip",
                "parameters": {"tracetype": "fusion.zip"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 12,
                "method": "AS_Cal_20220204",
                "point": 4,
                "test": {
                    "moduleA:tcd": {
                        "i": 0,
                        "elution_time": {"n": 0.0, "s": 0.02, "u": "s"},
                        "signal": {"n": 0.0, "s": 1.0, "u": None},
                    }
                },
            },
        ),
        (
            {  # ts4 - agilent ch file parse
                "folders": ["."],
                "suffix": "CH",
                "parameters": {"tracetype": "agilent.ch"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "method": "CO2RR_FTI_0.7mL_40uL_45dgr_36min.amx",
                "point": 0,
                "test": {
                    "RID1A": {
                        "i": 0,
                        "elution_time": {"n": 0.0675, "s": 0.0675, "u": "s"},
                        "signal": {"n": 0.39, "s": 0.01, "u": "nRIU"},
                    }
                },
            },
        ),
        (
            {  # ts5 - agilent dx file unzip & parse
                "folders": ["."],
                "suffix": "dx",
                "parameters": {"tracetype": "agilent.dx"},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "method": "CO2RR_FTI_0.7mL_40uL_45dgr_36min.amx",
                "point": 0,
                "test": {
                    "RID1A": {
                        "i": 10,
                        "elution_time": {"n": 2.2276485, "s": 0.0675, "u": "s"},
                        "signal": {"n": -1.6, "s": 0.01, "u": "nRIU"},
                    }
                },
            },
        ),
    ],
)
def test_datagram_from_chromtrace(input, ts, datadir):
    os.chdir(datadir)
    dg = datagram_from_input(input, "chromtrace", datadir)
    standard_datagram_test(dg, ts)
    if isinstance(ts["step"], str):
        step = dg[ts["step"]]
    else:
        step = dg[list(dg.children.keys())[ts["step"]]]
    for k, v in ts["test"].items():
        for kk in {"signal", "elution_time"}:
            ret = dg_get_quantity(step, k, col=kk, utsrow=ts["point"])
            print(f"{v[kk]=}")
            print(f"{ret=}")
            compare_result_dicts(
                {"n": ret["n"][v["i"]], "s": ret["s"][v["i"]], "u": ret["u"]},
                v[kk],
            )


@pytest.mark.parametrize(
    "input",
    [
        (
            {  # ts0 - ch file parse, method, and integration
                "folders": ["."],
                "suffix": "CH",
                "parameters": {"tracetype": "agilent.ch"},
            }
        ),
        (
            {  # ts1 - dx file unzip, parse, method, integration from file
                "folders": ["."],
                "suffix": "dx",
                "parameters": {"tracetype": "agilent.dx"},
            }
        ),
    ],
)
def test_chromtrace_compare_raw_values(input, datadir):
    os.chdir(datadir)
    dg = datagram_from_input(input, "chromtrace", datadir)
    with open("yvals.json", "r") as infile:
        ref = json.load(infile)["traces"]
    for trace, v in ref.items():
        for k in {"signal", "elution_time"}:
            ret = dg_get_quantity(dg["0"], trace, col=k, utsrow=0)
            compare_result_dicts(ret, v[k])
