import pytest
import os
import numpy as np
import json
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
)


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    if testspec["method"] is not None:
        assert step["metadata"]["params"]["method"].endswith(testspec["method"])
    tstep = step["data"][testspec["point"]]
    print(tstep["raw"]["traces"].keys())
    for k, v in testspec["test"].items():
        t = {
            "n": tstep["raw"]["traces"][k]["t"]["n"][v["i"]],
            "s": tstep["raw"]["traces"][k]["t"]["s"][v["i"]],
            "u": tstep["raw"]["traces"][k]["t"]["u"],
        }
        compare_result_dicts(t, v["t"])
        y = {
            "n": tstep["raw"]["traces"][k]["y"]["n"][v["i"]],
            "s": tstep["raw"]["traces"][k]["y"]["s"][v["i"]],
            "u": tstep["raw"]["traces"][k]["y"]["u"],
        }
        compare_result_dicts(y, v["y"])


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
                        "t": {"n": 100.002, "s": 0.100002, "u": "s"},
                        "y": {"n": 2.085281, "s": 0.000130, "u": "pA"},
                    },
                    "1": {
                        "i": 1000,
                        "t": {"n": 100.002, "s": 0.100002, "u": "s"},
                        "y": {"n": 55.892435, "s": 0.000130, "u": "V"},
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
                        "t": {"n": 2.15999999, "s": 0.06, "u": "s"},
                        "y": {"n": 488830.0, "s": 0.001, "u": " "},
                    },
                    "FID2B.ch": {
                        "i": 10,
                        "t": {"n": 2.15999999, "s": 0.06, "u": "s"},
                        "y": {"n": 42430.0, "s": 0.001, "u": " "},
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
                        "t": {"n": 2.0, "s": 0.02, "u": "s"},
                        "y": {"n": 1566.0, "s": 1.0, "u": " "},
                    },
                    "moduleB:tcd": {
                        "i": 100,
                        "t": {"n": 2.0, "s": 0.02, "u": "s"},
                        "y": {"n": -1412.0, "s": 1.0, "u": " "},
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
                        "t": {"n": 0.0, "s": 0.02, "u": "s"},
                        "y": {"n": 0.0, "s": 1.0, "u": " "},
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
                        "t": {"n": 0.0675, "s": 0.0675, "u": "s"},
                        "y": {"n": 0.39, "s": 0.01, "u": "nRIU"},
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
                        "t": {"n": 2.2276485, "s": 0.0675, "u": "s"},
                        "y": {"n": -1.6, "s": 0.01, "u": "nRIU"},
                    }
                },
            },
        ),
    ],
)
def test_datagram_from_chromtrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "chromtrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)


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
    ret = datagram_from_input(input, "chromtrace", datadir)
    with open("yvals.json", "r") as infile:
        ref = json.load(infile)["traces"]
    for k, v in ret["steps"][0]["data"][0]["raw"]["traces"].items():
        for kk in ["t", "y"]:
            for kkk in ["n", "s"]:
                assert np.allclose(ref[k][kk][kkk], v[kk][kkk])
