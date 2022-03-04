import pytest
import os
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
)
import numpy as np
import json


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    assert step["metadata"]["params"]["method"].endswith(testspec["method"])
    tstep = step["data"][testspec["point"]]
    for k, v in testspec["peaks"].items():
        compare_result_dicts(tstep["derived"]["peaks"]["LC"][k]["A"], v)


refvals = {
    "a": {"n": 4203.5798851, "s": 3.15755412, "u": " "},
    "b": {"n": 23349.8855948, "s": 16.2068347, "u": " "},
    "c": {"n": 71369.5831322, "s": 44.2360720, "u": " "},
    "d": {"n": 13119.4243886, "s": 7.23123702, "u": " "},
}


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - ch file parse, method, and integration
                "folders": ["."],
                "suffix": "CH",
                "parameters": {
                    "tracetype": "agilent.ch",
                    "calfile": "lc_calfile.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "method": "CO2RR_FTI_0.7mL_40uL_45dgr_36min.amx",
                "point": 0,
                "peaks": refvals,
            },
        ),
        (
            {  # ts1 - dx file unzip, parse, method, integration from file
                "folders": ["."],
                "suffix": "dx",
                "parameters": {
                    "tracetype": "agilent.dx",
                    "calfile": "lc_calfile.json",
                },
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "method": "CO2RR_FTI_0.7mL_40uL_45dgr_36min.amx",
                "point": 0,
                "peaks": refvals,
            },
        ),
    ],
)
def test_datagram_from_lctrace(input, ts, datadir):
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
                "parameters": {
                    "tracetype": "agilent.ch",
                    "calfile": "lc_calfile.json",
                },
            }
        ),
        (
            {  # ts1 - dx file unzip, parse, method, integration from file
                "folders": ["."],
                "suffix": "dx",
                "parameters": {
                    "tracetype": "agilent.dx",
                    "calfile": "lc_calfile.json",
                },
            }
        ),
    ],
)
def test_compare_raw_values(input, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "chromtrace", datadir)
    with open("yvals.json", "r") as infile:
        ref = json.load(infile)["traces"]
    for k, v in ret["steps"][0]["data"][0]["raw"]["traces"].items():
        for kk in ["t", "y"]:
            for kkk in ["n", "s"]:
                assert np.allclose(ref[k][kk][kkk], v[kk][kkk])
