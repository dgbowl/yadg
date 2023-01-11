import pytest
import os
import json
import numpy as np
from tests.utils import (
    datagram_from_input,
    standard_datagram_test,
    compare_result_dicts,
)


def special_datagram_test(datagram, testspec):
    step = datagram["steps"][testspec["step"]]
    tstep = step["data"][testspec["point"]]
    assert (
        len(tstep["raw"]["traces"]["S11"]["f"]["n"]) == testspec["tracelen"]
        and len(tstep["raw"]["traces"]["S11"]["Re(Γ)"]["n"]) == testspec["tracelen"]
        and len(tstep["raw"]["traces"]["S11"]["Im(Γ)"]["n"]) == testspec["tracelen"]
    ), "length of 'f', 'Re(Γ)', 'Im(Γ)' not as prescribed."
    print(tstep["raw"]["traces"].keys())
    for k, v in testspec["test"].items():
        t = {
            "n": tstep["raw"]["traces"][k]["f"]["n"][v["i"]],
            "s": tstep["raw"]["traces"][k]["f"]["s"][v["i"]],
            "u": tstep["raw"]["traces"][k]["f"]["u"],
        }
        compare_result_dicts(t, v["f"])
        re = {
            "n": tstep["raw"]["traces"][k]["Re(Γ)"]["n"][v["i"]],
            "s": tstep["raw"]["traces"][k]["Re(Γ)"]["s"][v["i"]],
            "u": tstep["raw"]["traces"][k]["Re(Γ)"]["u"],
        }
        compare_result_dicts(re, v["re"])
        im = {
            "n": tstep["raw"]["traces"][k]["Im(Γ)"]["n"][v["i"]],
            "s": tstep["raw"]["traces"][k]["Im(Γ)"]["s"][v["i"]],
            "u": tstep["raw"]["traces"][k]["Im(Γ)"]["u"],
        }
        compare_result_dicts(im, v["im"])


@pytest.mark.parametrize(
    "input, ts",
    [
        (
            {  # ts0 - 01-inert
                "folders": ["data_3.1.0/01-inert"],
                "parameters": {},
            },
            {
                "nsteps": 1,
                "step": 0,
                "nrows": 1,
                "point": 0,
                "tracelen": 20001,
                "npeaks": 2,
                "peak": 0,
                "test": {
                    "S11": {
                        "i": 0,
                        "f": {"n": 7.1e9, "s": 1e3, "u": "Hz"},
                        "re": {"n": -0.0192804, "s": 1e-8, "u": " "},
                        "im": {"n": 0.9448405, "s": 1e-7, "u": " "},
                    }
                },
            },
        )
    ],
)
def test_datagram_from_qftrace(input, ts, datadir):
    os.chdir(datadir)
    ret = datagram_from_input(input, "qftrace", datadir)
    standard_datagram_test(ret, ts)
    special_datagram_test(ret, ts)


def test_qftrace_compare_raw_values(datadir):
    input = {
        "folders": ["data_3.1.0/01-inert"],
        "parameters": {},
    }
    os.chdir(datadir)
    ret = datagram_from_input(input, "qftrace", datadir)
    with open("yvals.json", "r") as infile:
        ref = json.load(infile)["traces"]
    for k, v in ret["steps"][0]["data"][0]["raw"]["traces"].items():
        for kk in ["f", "Re(Γ)", "Im(Γ)"]:
            for kkk in ["n", "s"]:
                assert np.allclose(ref[k][kk][kkk], v[kk][kkk])
